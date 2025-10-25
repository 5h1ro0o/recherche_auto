#!/usr/bin/env python3
# backend/check_dependencies.py
"""
Script de vérification des dépendances du projet
Vérifie que tous les imports nécessaires sont disponibles
"""

import sys
from typing import List, Tuple

def check_import(module_name: str, package_name: str = None, extra_info: str = "") -> Tuple[bool, str]:
    """
    Vérifie si un module peut être importé
    
    Args:
        module_name: Nom du module à importer
        package_name: Nom du package pip (si différent du module)
        extra_info: Information supplémentaire pour l'installation
        
    Returns:
        Tuple (success, message)
    """
    try:
        __import__(module_name)
        return True, f"✅ {module_name}"
    except ImportError:
        pkg = package_name or module_name
        cmd = f"pip install {pkg}"
        if extra_info:
            cmd += f" && {extra_info}"
        return False, f"❌ {module_name} - Installer avec: {cmd}"


def main():
    """Fonction principale de vérification"""
    print("="*70)
    print("🔍 VÉRIFICATION DES DÉPENDANCES")
    print("="*70)
    print()
    
    checks: List[Tuple[str, str, str]] = [
        # (module, package_pip, extra_info)
        ("fastapi", "fastapi", ""),
        ("uvicorn", "uvicorn[standard]", ""),
        ("sqlalchemy", "SQLAlchemy", ""),
        ("alembic", "alembic", ""),
        ("psycopg2", "psycopg2-binary", ""),
        ("pydantic", "pydantic", ""),
        ("elasticsearch", "elasticsearch>=8.0.0", ""),
        ("redis", "redis", ""),
        ("jose", "python-jose[cryptography]", ""),
        ("passlib", "passlib[bcrypt]", ""),
        ("openai", "openai>=1.0.0", ""),
        ("celery", "celery[redis]>=5.3.0", ""),
        ("playwright", "playwright>=1.41.0", "playwright install chromium"),
        ("bs4", "beautifulsoup4>=4.12.0", ""),
        ("fake_useragent", "fake-useragent>=1.4.0", ""),
        ("httpx", "httpx[http2]>=0.25.0", ""),
    ]
    
    results = []
    missing = []
    
    print("📦 Vérification des packages Python...")
    print()
    
    for module, package, extra in checks:
        success, message = check_import(module, package, extra)
        results.append((success, message))
        if not success:
            missing.append((package, extra))
        print(f"  {message}")
    
    print()
    print("="*70)
    
    # Résumé
    total = len(checks)
    installed = sum(1 for success, _ in results if success)
    missing_count = total - installed
    
    print(f"📊 RÉSUMÉ: {installed}/{total} packages installés")
    
    if missing_count == 0:
        print()
        print("🎉 TOUTES LES DÉPENDANCES SONT INSTALLÉES !")
        print()
        return 0
    else:
        print()
        print(f"⚠️  {missing_count} package(s) manquant(s)")
        print()
        print("📝 COMMANDES D'INSTALLATION:")
        print()
        
        # Grouper les commandes pip install
        pip_packages = [pkg for pkg, extra in missing if not extra]
        if pip_packages:
            print(f"  pip install {' '.join(pip_packages)}")
            print()
        
        # Commandes avec extras
        for pkg, extra in missing:
            if extra:
                print(f"  pip install {pkg}")
                print(f"  {extra}")
                print()
        
        print("="*70)
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())