#!/usr/bin/env python3
"""
Script de test pour identifier les sélecteurs CSS actuels des sites
"""

import sys
from playwright.sync_api import sync_playwright
import time

def test_leboncoin():
    """Teste LeBonCoin et affiche les sélecteurs trouvés"""
    print("\n" + "="*60)
    print("TEST LEBONCOIN")
    print("="*60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False pour voir
        page = browser.new_page()

        print("📍 Navigation vers LeBonCoin...")
        page.goto("https://www.leboncoin.fr/recherche?category=2&text=voiture", wait_until='domcontentloaded')
        time.sleep(5)  # Attendre le chargement

        # Tester différents sélecteurs
        selectors_to_test = [
            '[data-qa-id="aditem_container"]',
            'article',
            '[data-testid="listing"]',
            '.styles_adCard__I2Jmi',
            'a[href*="/ad/"]',
            'div[data-qa-id]',
            'section article',
            '.ad-card'
        ]

        for selector in selectors_to_test:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"✅ '{selector}' : {len(elements)} éléments trouvés")
                else:
                    print(f"❌ '{selector}' : 0 éléments")
            except Exception as e:
                print(f"❌ '{selector}' : Erreur - {e}")

        # Sauvegarder le HTML pour analyse
        html = page.content()
        with open('leboncoin_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("\n💾 HTML sauvegardé dans leboncoin_debug.html")

        input("\nAppuyez sur Entrée pour continuer...")
        browser.close()


def test_autoscout24():
    """Teste AutoScout24 et affiche les sélecteurs trouvés"""
    print("\n" + "="*60)
    print("TEST AUTOSCOUT24")
    print("="*60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("📍 Navigation vers AutoScout24...")
        page.goto("https://www.autoscout24.fr/lst?sort=standard&desc=0&atype=C&ustate=N,U&size=20",
                  wait_until='domcontentloaded')
        time.sleep(5)

        # Gérer les cookies
        try:
            accept_btn = page.query_selector('button:has-text("Accepter")')
            if accept_btn:
                accept_btn.click()
                time.sleep(2)
        except:
            pass

        # Tester différents sélecteurs
        selectors_to_test = [
            'article[data-testid="listing-item"]',
            'article.ListItem_article',
            'div[data-testid="search-listing"]',
            'a.ListItem_title',
            'article',
            'div[class*="ListItem"]',
            'a[href*="/annonces/"]',
            '[data-testid*="listing"]'
        ]

        for selector in selectors_to_test:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"✅ '{selector}' : {len(elements)} éléments trouvés")
                else:
                    print(f"❌ '{selector}' : 0 éléments")
            except Exception as e:
                print(f"❌ '{selector}' : Erreur - {e}")

        # Sauvegarder le HTML
        html = page.content()
        with open('autoscout24_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("\n💾 HTML sauvegardé dans autoscout24_debug.html")

        input("\nAppuyez sur Entrée pour fermer...")
        browser.close()


if __name__ == "__main__":
    print("\n🔍 SCRIPT DE TEST DES SÉLECTEURS CSS")
    print("\nCe script va:")
    print("1. Ouvrir les sites dans un navigateur visible")
    print("2. Tester différents sélecteurs CSS")
    print("3. Sauvegarder le HTML pour analyse")

    choice = input("\nQue voulez-vous tester?\n1. LeBonCoin\n2. AutoScout24\n3. Les deux\nChoix (1/2/3): ")

    if choice in ['1', '3']:
        test_leboncoin()

    if choice in ['2', '3']:
        test_autoscout24()

    print("\n✅ Tests terminés!")
