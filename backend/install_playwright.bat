#!/bin/bash
# backend/install_playwright.sh
# Script pour installer Playwright et ses navigateurs

echo "🎭 Installation de Playwright..."

# Installer playwright si pas déjà fait
pip install playwright>=1.41.0

# Installer les navigateurs
echo "📦 Installation des navigateurs Chromium..."
playwright install chromium

# Installer les dépendances système (Linux uniquement)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Installation des dépendances système Linux..."
    playwright install-deps chromium
fi

echo "✅ Playwright installé avec succès!"
echo ""
echo "Pour tester, exécutez:"
echo "  python -c 'from playwright.sync_api import sync_playwright; print(\"OK\")'"