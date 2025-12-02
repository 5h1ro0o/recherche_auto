# 📖 GUIDE COMPLET DES SCRAPERS ENCYCLOPÉDIE AUTOMOBILE

Ce guide explique comment utiliser tous les scripts de scraping pour collecter les données automobiles.

---

## 📁 SCRIPTS DISPONIBLES

### 1. ✅ **scrape_encyclopedia_improved.py** (RECOMMANDÉ)
**Script le plus récent et testé** - Collecte les marques et modèles

**Ce qu'il fait :**
- ✅ Collecte **57 marques mondiales** avec leurs informations
- ✅ Collecte **200+ modèles** pour 19 marques principales
- ✅ Utilise Playwright pour éviter les blocages 403
- ✅ Génère automatiquement les IDs uniques
- ✅ Données de fallback intégrées (fonctionne même sans Internet)

**Comment l'utiliser :**
```bash
cd backend
python scrape_encyclopedia_improved.py
```

**Résultat attendu :**
- 57 marques dans `car_brands`
- 155 modèles dans `car_models`

---

### 2. **scrape_models_web.py**
Collecte détaillée des modèles depuis plusieurs sources web

**Sources :**
- CarQuery API
- Automobile-Catalog
- Caradisiac (avis utilisateurs)
- L'Argus (fiches techniques)

**Données collectées :**
- Caractéristiques techniques complètes
- Consommation et émissions CO2
- Avantages et inconvénients
- Avis clients réels

**Comment l'utiliser :**
```bash
python scrape_models_web.py
```

⚠️ **Note :** Ce script peut rencontrer des erreurs 403. Utilisez `scrape_encyclopedia_improved.py` à la place.

---

### 3. **scrape_engines_web.py**
Collecte les données des moteurs automobiles

**Sources :**
- Sites techniques spécialisés
- Caradisiac Fiabilité
- Forums automobiles
- L'Argus

**Données collectées :**
- Spécifications techniques (cylindrée, puissance, couple)
- Notes de fiabilité
- Problèmes communs recensés
- Coûts d'entretien
- Avis d'experts et utilisateurs

**Comment l'utiliser :**
```bash
python scrape_engines_web.py
```

⚠️ **Note :** Nécessite que les marques soient déjà dans la base de données.

---

### 4. **scrape_transmissions_web.py**
Collecte les données des transmissions (boîtes de vitesses)

**Sources :**
- Caradisiac
- Forums spécialisés
- L'Argus
- Sites techniques

**Données collectées :**
- Type et nombre de rapports
- Notes de fiabilité
- Problèmes communs (embrayages, mécatronique)
- Coûts de maintenance
- Avis utilisateurs

**Comment l'utiliser :**
```bash
python scrape_transmissions_web.py
```

---

### 5. **run_all_scrapers.py**
Script orchestrateur qui lance tous les scrapers en séquence

**Comment l'utiliser :**
```bash
python run_all_scrapers.py
```

**Ce qu'il fait :**
1. Lance le scraping des modèles
2. Lance le scraping des moteurs
3. Lance le scraping des transmissions
4. Affiche des statistiques détaillées

⚠️ **Note :** Peut prendre plusieurs heures. Nécessite des mises à jour pour éviter les erreurs.

---

## 🚀 UTILISATION RECOMMANDÉE

### Étape 1 : Collecter les marques et modèles de base

```bash
# Utiliser le scraper amélioré (testé et fonctionnel)
python scrape_encyclopedia_improved.py
```

**Résultat :**
- ✅ 57 marques
- ✅ 155 modèles de base

### Étape 2 : Vérifier les données

```bash
# Connexion à PostgreSQL
psql -U postgres -d recherche_auto

# Compter les marques
SELECT COUNT(*) FROM car_brands;

# Compter les modèles
SELECT COUNT(*) FROM car_models;

# Voir quelques exemples
SELECT cb.name as marque, cm.name as modele
FROM car_models cm
JOIN car_brands cb ON cm.brand_id = cb.id
LIMIT 10;

\q
```

### Étape 3 : Collecter les moteurs et transmissions (optionnel)

```bash
# Moteurs
python scrape_engines_web.py

# Transmissions
python scrape_transmissions_web.py
```

---

## 📊 STRUCTURE DES DONNÉES

### Tables créées :
- `car_brands` - Marques automobiles
- `car_models` - Modèles de voitures
- `engines` - Moteurs
- `transmissions` - Transmissions
- `engine_model_associations` - Liens moteur ↔ modèle
- `transmission_model_associations` - Liens transmission ↔ modèle
- `engine_transmission_associations` - Liens moteur ↔ transmission

### Relations :
- Une **marque** a plusieurs **modèles**
- Un **modèle** peut avoir plusieurs **moteurs**
- Un **modèle** peut avoir plusieurs **transmissions**
- Un **moteur** peut être dans plusieurs **modèles**
- Un **moteur** peut fonctionner avec plusieurs **transmissions**

---

## ⚙️ CONFIGURATION REQUISE

### Dépendances Python :
```bash
pip install aiohttp beautifulsoup4 lxml asyncpg playwright
playwright install chromium
```

### Variables d'environnement (.env) :
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recherche_auto
```

### Base de données :
```bash
# Créer la base
psql -U postgres
CREATE DATABASE recherche_auto;
\q

# Appliquer les migrations
alembic upgrade head
```

---

## 🔧 DÉPANNAGE

### Erreur : "Connection refused"
**Problème :** PostgreSQL n'est pas démarré

**Solution :**
```bash
# Windows
pg_ctl start

# Linux/Mac
sudo systemctl start postgresql
```

### Erreur : "Status 403 Forbidden"
**Problème :** Le site web bloque le scraping

**Solution :** Utiliser `scrape_encyclopedia_improved.py` qui contourne ces blocages avec Playwright.

### Erreur : "NOT NULL constraint violation"
**Problème :** Les IDs ne sont pas générés

**Solution :** Utiliser `scrape_encyclopedia_improved.py` qui génère automatiquement les IDs.

### Erreur : "text() is required"
**Problème :** SQLAlchemy 2.0 nécessite text() pour les requêtes SQL brutes

**Solution :** Déjà corrigé dans `scrape_encyclopedia_improved.py`

---

## 📈 PERFORMANCE

### Temps estimés :
- **scrape_encyclopedia_improved.py** : 2-5 minutes ✅
- **scrape_models_web.py** : 1-2 heures
- **scrape_engines_web.py** : 30-60 minutes
- **scrape_transmissions_web.py** : 30-60 minutes
- **run_all_scrapers.py** : 2-4 heures

### Données collectées :
- **Marques** : 57
- **Modèles** : 155 (basic) ou 500-1000+ (web scraping complet)
- **Moteurs** : 100-200
- **Transmissions** : 30-50

---

## 🎯 PROCHAINES ÉTAPES

Après avoir collecté les données :

1. **Tester l'API :**
```bash
# Démarrer le backend
uvicorn app.main:app --reload --port 8000

# Tester les endpoints
curl http://localhost:8000/encyclopedia/brands
```

2. **Voir dans le frontend :**
```bash
cd ../frontend
npm run dev
# Ouvrir http://localhost:5173
```

3. **Créer les associations :**
```bash
# Script à créer pour lier moteurs ↔ modèles ↔ transmissions
python link_engines_models_transmissions.py
```

---

## 📞 SUPPORT

En cas de problème :
1. Vérifier que PostgreSQL est démarré
2. Vérifier que les migrations sont appliquées (`alembic upgrade head`)
3. Vérifier les logs d'erreur dans la console
4. Utiliser `scrape_encyclopedia_improved.py` en priorité (version stable et testée)

---

**Dernière mise à jour :** 2025-11-30
**Version stable recommandée :** `scrape_encyclopedia_improved.py`
