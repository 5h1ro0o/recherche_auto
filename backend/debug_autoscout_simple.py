#!/usr/bin/env python3
"""
Script de debug SIMPLE pour comprendre pourquoi parse_listing retourne None
"""

import sys
import logging
from playwright.sync_api import sync_playwright
import time
import re

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_parse_logic():
    """Tester la logique de parse_listing étape par étape"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

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

        page.wait_for_load_state('networkidle', timeout=30000)
        time.sleep(2)

        # Trouver les annonces
        elements = page.query_selector_all('div[class*="ListItem"]')
        logger.info(f"✅ Trouvé {len(elements)} éléments\n")

        # Analyser le PREMIER élément en détail
        if len(elements) > 0:
            element = elements[0]
            logger.info("="*80)
            logger.info("ANALYSE DÉTAILLÉE DU PREMIER ÉLÉMENT")
            logger.info("="*80)

            # ÉTAPE 1: Trouver le lien
            logger.info("\n--- ÉTAPE 1: CHERCHER LE LIEN ---")
            try:
                tag_name = element.evaluate('el => el.tagName.toLowerCase()')
                logger.info(f"Tag de l'élément: {tag_name}")
            except Exception as e:
                logger.error(f"Erreur evaluate tag: {e}")

            link = element.query_selector('a[href*="/annonces/"]')
            logger.info(f"Lien avec /annonces/: {link}")

            if not link:
                link = element.query_selector('a')
                logger.info(f"Premier lien <a> trouvé: {link}")

            if link:
                href = link.get_attribute('href')
                logger.info(f"✅ Href du lien: {href}")

                # Vérifier le contenu de l'URL
                if '/annonces/' in href:
                    logger.info("✅ L'URL contient '/annonces/'")
                else:
                    logger.warning(f"❌ L'URL ne contient PAS '/annonces/' - c'est pourquoi le parsing échoue!")
                    logger.warning(f"   L'URL est: {href}")
            else:
                logger.error("❌ AUCUN LIEN TROUVÉ - c'est pourquoi le parsing échoue!")

            # ÉTAPE 2: Extraire le texte
            logger.info("\n--- ÉTAPE 2: EXTRAIRE LE TEXTE ---")
            try:
                full_text = element.inner_text()
                logger.info(f"Texte complet ({len(full_text)} caractères):")
                logger.info(full_text[:500])
            except Exception as e:
                logger.error(f"Erreur extraction texte: {e}")
                full_text = ""

            # ÉTAPE 3: Chercher le titre
            logger.info("\n--- ÉTAPE 3: CHERCHER LE TITRE ---")
            title_selectors = ['h2', 'h3', '[data-testid*="title"]', '[class*="title"]', '[class*="Title"]', 'a']
            title = None
            for selector in title_selectors:
                title_elem = element.query_selector(selector)
                if title_elem:
                    try:
                        title_text = title_elem.inner_text().strip()
                        logger.info(f"  Sélecteur '{selector}': '{title_text}'")
                        if title_text and len(title_text) > 3:
                            title = title_text
                            logger.info(f"  ✅ TITRE TROUVÉ: '{title}'")
                            break
                    except Exception as e:
                        logger.debug(f"  Erreur: {e}")

            if not title and link:
                title = link.get_attribute('title') or link.get_attribute('aria-label')
                if title:
                    logger.info(f"  ✅ Titre depuis attribut du lien: '{title}'")

            if not title:
                logger.error("  ❌ AUCUN TITRE TROUVÉ - c'est pourquoi le parsing échoue!")

            # ÉTAPE 4: Extraire le prix
            logger.info("\n--- ÉTAPE 4: EXTRAIRE LE PRIX ---")
            price_patterns = [
                r'(\d{1,3}(?:\s?\d{3})*)\s*€',
                r'€\s*(\d{1,3}(?:\s?\d{3})*)',
            ]
            for pattern in price_patterns:
                match = re.search(pattern, full_text)
                if match:
                    price = match.group(1).replace(' ', '')
                    logger.info(f"  ✅ Prix trouvé: {price} € (pattern: {pattern})")
                    break
            else:
                logger.warning("  ⚠️ Aucun prix trouvé")

            # ÉTAPE 5: Année
            logger.info("\n--- ÉTAPE 5: EXTRAIRE L'ANNÉE ---")
            year_match = re.search(r'\b(19\d{2}|20[0-3]\d)\b', full_text)
            if year_match:
                year = int(year_match.group(1))
                logger.info(f"  ✅ Année trouvée: {year}")
            else:
                logger.warning("  ⚠️ Aucune année trouvée")

            # RÉSUMÉ
            logger.info("\n" + "="*80)
            logger.info("RÉSUMÉ DU PARSING")
            logger.info("="*80)
            logger.info(f"Lien trouvé: {link is not None}")
            if link:
                logger.info(f"  URL: {href}")
                logger.info(f"  Contient '/annonces/': {'/annonces/' in href if href else False}")
            logger.info(f"Titre trouvé: {title is not None}")
            if title:
                logger.info(f"  Titre: {title}")
            logger.info(f"\n🔴 LE PARSING RETOURNE None SI:")
            logger.info(f"   - Pas de lien AVEC '/annonces/' dans l'URL")
            logger.info(f"   - OU pas de titre (len < 3)")

        logger.info("\n⏸️  Navigateur reste ouvert 30 secondes...")
        time.sleep(30)

        browser.close()
        logger.info("✅ Debug terminé!")

if __name__ == '__main__':
    debug_parse_logic()
