#!/usr/bin/env python3
"""
Script pour appliquer automatiquement les transformations du design prestigieux
sur toutes les pages React restantes.
"""
import re
import os
from pathlib import Path

# Transformations de couleurs
COLOR_REPLACEMENTS = {
    "'#FFFFFF'": "'var(--white)'",
    '"#FFFFFF"': '"var(--white)"',
    "'white'": "'var(--white)'",
    '"white"': '"var(--white)"',
    "'#222222'": "'var(--text-primary)'",
    '"#222222"': '"var(--text-primary)"',
    "'#111111'": "'var(--text-primary)'",
    '"#111111"': '"var(--text-primary)"',
    "'#666666'": "'var(--text-secondary)'",
    '"#666666"': '"var(--text-secondary)"',
    "'#999999'": "'var(--text-muted)'",
    '"#999999"': '"var(--text-muted)"',
    "'#1A1A1A'": "'var(--gray-900)'",
    '"#1A1A1A"': '"var(--gray-900)"',
    "'#2A2A2A'": "'var(--gray-800)'",
    '"#2A2A2A"': '"var(--gray-800)"',
    "'#F9FAFB'": "'var(--gray-50)'",
    '"#F9FAFB"': '"var(--gray-50)"',
    "'#FAFAFA'": "'var(--gray-50)'",
    '"#FAFAFA"': '"var(--gray-50)"',
    "'#E5E7EB'": "'var(--border-light)'",
    '"#E5E7EB"': '"var(--border-light)"',
    "'#EEEEEE'": "'var(--border-light)'",
    '"#EEEEEE"': '"var(--border-light)"',
    "'#DC2626'": "'var(--red-accent)'",
    '"#DC2626"': '"var(--red-accent)"',
    "'#EF4444'": "'var(--red-accent)'",
    '"#EF4444"': '"var(--red-accent)"',
    "'#B91C1C'": "'var(--red-accent)'",
    '"#B91C1C"': '"var(--red-accent)"',
}

# Transformations de spacing
SPACING_REPLACEMENTS = {
    "'4px'": "'var(--space-1)'",
    '"4px"': '"var(--space-1)"',
    "'8px'": "'var(--space-2)'",
    '"8px"': '"var(--space-2)"',
    "'12px'": "'var(--space-3)'",
    '"12px"': '"var(--space-3)"',
    "'16px'": "'var(--space-4)'",
    '"16px"': '"var(--space-4)"',
    "'20px'": "'var(--space-5)'",
    '"20px"': '"var(--space-5)"',
    "'24px'": "'var(--space-6)'",
    '"24px"': '"var(--space-6)"',
    "'28px'": "'var(--space-7)'",
    '"28px"': '"var(--space-7)"',
    "'32px'": "'var(--space-8)'",
    '"32px"': '"var(--space-8)"',
    "'40px'": "'var(--space-10)'",
    '"40px"': '"var(--space-10)"',
    "'48px'": "'var(--space-12)'",
    '"48px"': '"var(--space-12)"',
    "'60px'": "'var(--space-16)'",
    '"60px"': '"var(--space-16)"',
    "'64px'": "'var(--space-16)'",
    '"64px"': '"var(--space-16)"',
    "'80px'": "'var(--space-20)'",
    '"80px"': '"var(--space-20)"',
}

# Emojis à supprimer
EMOJIS_TO_REMOVE = [
    '🚗', '🔍', '🤖', '📚', '❤️', '💬', '⭐', '🏢', '👤', '🔧',
    '⏳', '✅', '📧', '✉️', '📱', '🔐', '🆔', '📅', '🚪', '🎯',
    '🔄', '⚠️', '📍', '🛣️', '⛽', '📊', '💰', '📭', '📎', '💼',
    '👥', '⛽', '⚙️', '🟠', '🔵', '⏱️', '🔔', '📈', '📉', '💡',
    '🎨', '🔗', '📝', '✏️', '🗑️', '📤', '📥', '🎁', '🏆', '🎉'
]

def transform_file(filepath):
    """Applique toutes les transformations à un fichier."""
    print(f"  Transformation de {filepath.name}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Supprimer les emojis
    for emoji in EMOJIS_TO_REMOVE:
        content = content.replace(emoji, '')

    # 2. Supprimer borderRadius
    content = re.sub(r"borderRadius:\s*['\"][\d]+px['\"],?\n?", "", content)
    content = re.sub(r"borderRadius:\s*['\"][\d.]+rem['\"],?\n?", "", content)

    # 3. Remplacer les couleurs
    for old, new in COLOR_REPLACEMENTS.items():
        content = content.replace(old, new)

    # 4. Remplacer les spacing
    for old, new in SPACING_REPLACEMENTS.items():
        content = content.replace(old, new)

    # 5. Nettoyer les espaces multiples et lignes vides en trop
    content = re.sub(r'\n\n\n+', '\n\n', content)

    # Écrire seulement si modifié
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"    ✅ {filepath.name} transformé")
        return True
    else:
        print(f"    ⏭️  {filepath.name} déjà à jour")
        return False

def main():
    """Fonction principale."""
    pages_dir = Path('/home/user/recherche_auto/frontend/src/Pages')

    # Liste des pages à transformer
    pages_to_transform = [
        'MessagesPage.jsx',
        'ConversationPage.jsx',
        'AssistedRequestDetailPage.jsx',
        'TinderProposalsPage.jsx',
        'VehiclePage.jsx',
        'EncyclopediaPage.jsx',
        'ExpertRequestDetailPage.jsx',
        'ExpertMissionsPage.jsx',
        'ExpertMarketPage.jsx',
        'ExpertVehicleSearchPage.jsx',
        'ExpertDashboard.jsx',
        'ProDashboard.jsx',
        'AdminDashboard.jsx',
    ]

    print("🎨 Début de la transformation automatique...")
    print(f"📁 Répertoire: {pages_dir}")
    print(f"📄 {len(pages_to_transform)} pages à transformer\n")

    transformed = 0
    skipped = 0

    for page_name in pages_to_transform:
        filepath = pages_dir / page_name
        if filepath.exists():
            if transform_file(filepath):
                transformed += 1
            else:
                skipped += 1
        else:
            print(f"  ⚠️  {page_name} introuvable")

    print(f"\n✨ Transformation terminée!")
    print(f"  ✅ {transformed} pages transformées")
    print(f"  ⏭️  {skipped} pages déjà à jour")
    print(f"\n📝 Vérifiez les changements avec: git diff frontend/src/Pages/")

if __name__ == '__main__':
    main()
