#!/usr/bin/env python3
"""
Script de debug pour AutoScout24
Va ouvrir le navigateur en mode visible et montrer exactement ce qui est extrait
"""

import sys
import logging
from playwright.sync_api import sync_playwright
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_autoscout():
    """Debug AutoScout24 scraping en mode visible"""

    with sync_playwright() as p:
        # Ouvrir navigateur VISIBLE
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        logger.info("🌐 Navigation vers AutoScout24...")
        url = "https://www.autoscout24.fr/lst?sort=standard&desc=0&atype=C&ustate=N,U&size=20"
        page.goto(url, wait_until='domcontentloaded', timeout=60000)

        # Accepter cookies
        try:
            time.sleep(2)
            cookie_button = page.query_selector('button[data-testid="accept-all-button"]')
            if cookie_button:
                cookie_button.click()
                logger.info("✅ Cookies acceptés")
                time.sleep(2)
        except:
            pass

        # Chercher les annonces
        logger.info("🔍 Recherche des annonces...")
        page.wait_for_load_state('networkidle', timeout=30000)
        time.sleep(3)

        # Sauvegarder screenshot
        page.screenshot(path='autoscout_debug_full.png', full_page=True)
        logger.info("📸 Screenshot sauvegardé: autoscout_debug_full.png")

        # Tester les sélecteurs
        selectors = [
            'div[class*="ListItem"]',
            'article',
            '[data-testid*="listing"]',
            'a[href*="/annonces/"]',
        ]

        for selector in selectors:
            elements = page.query_selector_all(selector)
            logger.info(f"Sélecteur '{selector}': {len(elements)} éléments")

        # Prendre le premier élément avec le sélecteur qui marche
        elements = page.query_selector_all('div[class*="ListItem"]')
        logger.info(f"\n{'='*80}")
        logger.info(f"ANALYSE DES {min(3, len(elements))} PREMIERS ÉLÉMENTS")
        logger.info(f"{'='*80}\n")

        for idx, element in enumerate(elements[:3], 1):
            logger.info(f"\n--- ÉLÉMENT {idx} ---")

            # HTML complet de l'élément
            html = element.inner_html()
            logger.info(f"HTML (premiers 500 chars):\n{html[:500]}...")

            # Texte complet
            try:
                full_text = element.inner_text()
                logger.info(f"\nTexte complet:\n{full_text}")
            except Exception as e:
                logger.error(f"Erreur extraction texte: {e}")

            # Chercher les liens
            links = element.query_selector_all('a')
            logger.info(f"\nNombre de liens <a>: {len(links)}")
            for link_idx, link in enumerate(links[:3], 1):
                href = link.get_attribute('href')
                link_text = link.inner_text()[:50] if link.inner_text() else ""
                logger.info(f"  Lien {link_idx}: {href} | Texte: {link_text}")

            # Chercher les titres
            titles = element.query_selector_all('h2, h3, [class*="title"], [class*="Title"]')
            logger.info(f"\nNombre de titres: {len(titles)}")
            for title_idx, title_elem in enumerate(titles, 1):
                title_text = title_elem.inner_text()
                logger.info(f"  Titre {title_idx}: {title_text}")

            # Chercher les prix
            import re
            price_patterns = [
                r'(\d{1,3}(?:\s?\d{3})*)\s*€',
                r'€\s*(\d{1,3}(?:\s?\d{3})*)',
            ]
            for pattern in price_patterns:
                matches = re.findall(pattern, full_text)
                if matches:
                    logger.info(f"Prix trouvé (pattern {pattern}): {matches}")

            # Screenshot de l'élément
            try:
                element.screenshot(path=f'autoscout_element_{idx}.png')
                logger.info(f"📸 Screenshot élément sauvegardé: autoscout_element_{idx}.png")
            except Exception as e:
                logger.warning(f"Impossible de screenshot l'élément: {e}")

        logger.info(f"\n{'='*80}")
        logger.info("⏸️  Navigateur restera ouvert 60 secondes pour inspection manuelle")
        logger.info(f"{'='*80}\n")

        time.sleep(60)

        browser.close()
        logger.info("✅ Debug terminé!")

if __name__ == '__main__':
    debug_autoscout()
