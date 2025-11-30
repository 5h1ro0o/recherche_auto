# 🌍 GUIDE COMPLET - SCRAPING TOTAL DE L'ENCYCLOPÉDIE AUTOMOBILE

## 🎯 OBJECTIF

Collecter **ABSOLUMENT TOUTES** les données automobiles depuis Internet :
- ✅ **TOUTES** les marques automobiles mondiales
- ✅ **TOUS** les modèles de toutes les marques
- ✅ **TOUTES** les caractéristiques techniques complètes
- ✅ **TOUS** les avis positifs et négatifs
- ✅ **TOUS** les moteurs avec fiabilité et problèmes
- ✅ **TOUTES** les transmissions avec retours utilisateurs

---

## 🚀 UTILISATION RAPIDE

### Option 1 : Tout en un seul script (RECOMMANDÉ)

```bash
cd backend
python scrape_everything.py
```

**Ce script lance tout automatiquement :**
1. Marques et modèles complets (1-2h)
2. Moteurs complets (1-2h)
3. Transmissions complètes (30-60min)
4. Associations (5-10min)

**Durée totale : 2-4 heures**

---

### Option 2 : Scripts individuels

Si vous voulez lancer les scrapers séparément :

```bash
# 1. Marques et modèles complets
python scrape_complete_data.py

# 2. Moteurs complets
python scrape_engines_complete.py

# 3. Transmissions complètes
python scrape_transmissions_complete.py
```

---

## 📋 SCRIPTS DISPONIBLES

### 🌟 **scrape_everything.py** - MASTER SCRIPT
Lance TOUS les scrapers dans le bon ordre

**Caractéristiques :**
- ✅ Scraping séquentiel optimisé
- ✅ Gestion d'erreurs robuste
- ✅ Statistiques en temps réel
- ✅ Résumé détaillé à la fin
- ✅ Interruption/Reprise possible (Ctrl+C)

---

### 🚗 **scrape_complete_data.py** - Marques & Modèles Complets

**Sources de données :**
- Automobile-Catalog.com (specs techniques)
- Caradisiac.com (avis utilisateurs, fiabilité)
- L'Argus.fr (caractéristiques, prix)
- Forums automobiles

**Données collectées par marque :**
- ✅ Nom, pays d'origine, année de création
- ✅ Description et historique
- ✅ Logo et informations visuelles

**Données collectées par modèle :**
- ✅ Nom complet du modèle
- ✅ Type de carrosserie (SUV, Berline, Break, etc.)
- ✅ **Caractéristiques techniques :**
  - Cylindrée moteur
  - Puissance (chevaux)
  - Couple (Nm)
  - Type de carburant
  - Type de transmission
  - Nombre de portes et places
  - Consommation moyenne
  - Émissions CO2
  - Accélération 0-100 km/h
  - Vitesse maximale

- ✅ **Avis et notes :**
  - Avantages (liste détaillée)
  - Inconvénients (liste détaillée)
  - Avis d'experts
  - Avis utilisateurs réels
  - Note globale de fiabilité

**Résultat attendu :**
- 100-200+ marques
- 1000-2000+ modèles avec specs complètes

---

### 🔧 **scrape_engines_complete.py** - Moteurs Complets

**Sources de données :**
- Sites techniques spécialisés
- Caradisiac Fiabilité
- Forums moteurs
- Bases de données techniques

**Données collectées par moteur :**
- ✅ Code moteur (ex: TCe 130, TDI 2.0, etc.)
- ✅ Fabricant
- ✅ Type de carburant (Essence, Diesel, Hybride, Électrique)
- ✅ **Spécifications techniques :**
  - Cylindrée (litres)
  - Puissance (chevaux)
  - Couple (Nm)
  - Nombre de cylindres
  - Configuration (En ligne, V, Boxer)
  - Aspiration (Turbo, Atmosphérique, Compresseur)

- ✅ **Fiabilité :**
  - Score de fiabilité sur 5
  - Problèmes communs recensés
  - Coût d'entretien estimé

- ✅ **Avis :**
  - Avantages techniques
  - Inconvénients connus
  - Retours d'expérience utilisateurs

**Résultat attendu :**
- 200-500+ moteurs différents
- Couvre tous les constructeurs

---

### ⚙️ **scrape_transmissions_complete.py** - Transmissions Complètes

**Sources de données :**
- Caradisiac
- Forums spécialisés transmissions
- Sites techniques

**Données collectées par transmission :**
- ✅ Type (Manuelle, Automatique, CVT, DSG, etc.)
- ✅ Nombre de rapports
- ✅ Code (DSG, EDC, 9G-Tronic, etc.)
- ✅ Fabricant (ZF, Aisin, Getrag, etc.)

- ✅ **Fiabilité :**
  - Score de fiabilité sur 5
  - Problèmes communs (embrayage, mécatronique, etc.)
  - Coût de maintenance

- ✅ **Avis :**
  - Avantages (souplesse, rapidité, etc.)
  - Inconvénients (à-coups, fragilité, etc.)
  - Retours utilisateurs

**Résultat attendu :**
- 50-100+ transmissions différentes
- Tous types confondus

---

## 🔍 TECHNOLOGIES UTILISÉES

### Anti-Détection
- **Playwright** : Navigateur réel automatisé
- **User-Agent rotation** : 4+ user agents différents
- **Délais aléatoires** : Entre 1-3 secondes
- **Scripts anti-détection** : Masquage de l'automation
- **Contexte réaliste** : Viewport, locale, timezone

### Extraction de données
- **Regex avancées** : Extraction des specs techniques
- **Sélecteurs CSS** : Navigation dans le DOM
- **Pattern matching** : Reconnaissance des formats
- **Déduplication** : Éviter les doublons

### Sauvegarde
- **Asyncpg** : Driver PostgreSQL async
- **SQLAlchemy** : ORM Python
- **Batch processing** : Sauvegarde par lots (20-50 items)
- **Error recovery** : Rollback en cas d'erreur

---

## 📊 RÉSULTATS ATTENDUS

Après un scraping complet, votre base de données contiendra :

```
📊 STATISTIQUES ESTIMÉES
┌────────────────────────┬──────────────┐
│ Marques                │  100-200+    │
│ Modèles                │  1000-2000+  │
│ Moteurs                │  200-500+    │
│ Transmissions          │  50-100+     │
│ Avis/Caractéristiques  │  10000+      │
└────────────────────────┴──────────────┘
```

### Par marque (exemple pour Renault) :

**Marque :** Renault
- Pays : France
- Fondée en : 1899
- Réputation : 4.2/5

**Modèles :**
- Clio (avec 5+ versions)
- Captur
- Megane
- Arkana
- Austral
- Kadjar
- Scenic
- Talisman
- Twingo
- + versions électriques (Zoe, Megane E-Tech)

**Moteurs :**
- TCe 90 (Essence, 3 cylindres, 90 ch, Turbo)
- TCe 130 (Essence, 4 cylindres, 130 ch, Turbo)
- Blue dCi 115 (Diesel, 4 cylindres, 115 ch, Turbo)
- E-Tech Hybrid (Hybride, 140-160 ch)
- + dizaines d'autres variantes

**Transmissions :**
- Manuelle 5 vitesses (JH3)
- Manuelle 6 vitesses (JR5)
- EDC 6 rapports (Automatique)
- EDC 7 rapports (Automatique)

**Caractéristiques par modèle :**
- Consommation : 4.2-6.5 L/100km
- CO2 : 95-145 g/km
- 0-100 km/h : 9.5-14 secondes
- Vitesse max : 165-200 km/h

**Avis :**
- ✅ Avantages : Économique, fiable, bon rapport qualité/prix
- ❌ Inconvénients : Finitions moyennes, insonorisation perfectible

---

## ⚙️ CONFIGURATION REQUISE

### Dépendances Python

```bash
pip install asyncio aiohttp beautifulsoup4 lxml
pip install playwright asyncpg sqlalchemy python-dotenv
playwright install chromium
```

### Variables d'environnement (.env)

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recherche_auto
```

### Base de données

```bash
# Créer la base
psql -U postgres
CREATE DATABASE recherche_auto;
\q

# Appliquer les migrations
cd backend
alembic upgrade head
```

---

## 🚨 IMPORTANT - ANTI-DÉTECTION

Ces scrapers utilisent plusieurs techniques pour éviter les blocages :

1. **Playwright (navigateur réel)** : Simule un vrai navigateur Chrome
2. **User-Agent aléatoire** : Rotation entre plusieurs user agents
3. **Délais aléatoires** : 1-3 secondes entre requêtes
4. **Headers réalistes** : Locale, timezone, viewport
5. **Scripts anti-détection** : Masque l'automation

**⚠️ Même avec ces protections :**
- Certains sites peuvent temporairement bloquer
- Le scraping peut prendre plusieurs heures
- Interruption possible avec Ctrl+C (données sauvegardées)

---

## 📈 PERFORMANCE

### Temps estimés :

| Script | Durée | Données collectées |
|--------|-------|-------------------|
| scrape_complete_data.py | 1-2h | Marques + Modèles complets |
| scrape_engines_complete.py | 1-2h | 200-500 moteurs |
| scrape_transmissions_complete.py | 30-60min | 50-100 transmissions |
| **TOTAL** | **2-4h** | **Encyclopédie complète** |

### Optimisations :

- ✅ Scraping séquentiel (évite surcharge)
- ✅ Sauvegarde par batch (performance DB)
- ✅ Déduplication automatique
- ✅ Cache pour éviter re-scraping

---

## 🔧 DÉPANNAGE

### Erreur : "Connection refused"

**Problème :** PostgreSQL pas démarré

**Solution :**
```bash
# Windows
pg_ctl start

# Linux/Mac
sudo systemctl start postgresql
```

---

### Erreur : "Status 403 Forbidden"

**Problème :** Site web bloque le scraping

**Solution :** C'est normal, les scrapers ont déjà :
- Protection anti-détection
- Rotation user agents
- Délais aléatoires

Si ça persiste : attendre quelques heures et relancer.

---

### Erreur : "Module not found"

**Problème :** Dépendances manquantes

**Solution :**
```bash
pip install -r requirements.txt
pip install playwright asyncpg
playwright install chromium
```

---

### Le scraping est très lent

**Normal !** Le scraping complet prend 2-4 heures car :
- Collecte de milliers de pages web
- Délais anti-détection (1-3s entre requêtes)
- Extraction et parsing des données
- Sauvegarde en base de données

**💡 Astuce :** Lancez le script et laissez-le tourner en arrière-plan.

---

### Interruption (Ctrl+C)

**Pas de panique !**
- Les données déjà collectées sont sauvegardées
- Vous pouvez relancer le script
- Il évitera les doublons (vérification en base)

---

## ✅ VÉRIFICATION DES DONNÉES

Après le scraping, vérifiez les résultats :

```bash
psql -U postgres -d recherche_auto

-- Compter les marques
SELECT COUNT(*) FROM car_brands;

-- Compter les modèles
SELECT COUNT(*) FROM car_models;

-- Compter les moteurs
SELECT COUNT(*) FROM engines;

-- Compter les transmissions
SELECT COUNT(*) FROM transmissions;

-- Voir les modèles avec le plus de caractéristiques
SELECT
    cb.name as marque,
    cm.name as modele,
    cm.horsepower,
    cm.fuel_type,
    cm.body_type
FROM car_models cm
JOIN car_brands cb ON cm.brand_id = cb.id
WHERE cm.horsepower IS NOT NULL
ORDER BY cm.horsepower DESC
LIMIT 20;

-- Voir les moteurs les plus fiables
SELECT
    code,
    manufacturer,
    reliability_score,
    horsepower
FROM engines
WHERE reliability_score >= 4
ORDER BY reliability_score DESC, horsepower DESC
LIMIT 20;

\q
```

---

## 🎯 APRÈS LE SCRAPING

Une fois toutes les données collectées :

### 1. Vérifier les données (ci-dessus)

### 2. Créer les associations

```bash
python link_engines_models.py  # À créer
```

### 3. Démarrer l'API

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Tester les endpoints

```bash
curl http://localhost:8000/encyclopedia/brands
curl http://localhost:8000/encyclopedia/models?brand_id=renault
curl http://localhost:8000/encyclopedia/engines?manufacturer=Renault
```

### 5. Lancer le frontend

```bash
cd ../frontend
npm run dev
```

Ouvrir : `http://localhost:5173`

---

## 📞 SUPPORT

En cas de problème :

1. ✅ Vérifier PostgreSQL est démarré
2. ✅ Vérifier migrations appliquées (`alembic upgrade head`)
3. ✅ Vérifier `.env` avec `DATABASE_URL`
4. ✅ Vérifier dépendances installées
5. ✅ Vérifier connexion Internet
6. ✅ Attendre quelques heures si 403 (rate limiting)

---

## 🎉 RÉSULTAT FINAL

Après le scraping complet, vous aurez **l'encyclopédie automobile la plus complète** avec :

- ✅ **Centaines de marques** du monde entier
- ✅ **Milliers de modèles** avec specs techniques complètes
- ✅ **Centaines de moteurs** avec fiabilité et problèmes recensés
- ✅ **Dizaines de transmissions** avec retours utilisateurs
- ✅ **Milliers d'avis** positifs et négatifs réels
- ✅ **Caractéristiques techniques** exhaustives
- ✅ **Notes de fiabilité** basées sur retours réels

**Une vraie mine d'or pour les passionnés d'automobile ! 🚗✨**

---

**Dernière mise à jour :** 2025-11-30
**Version :** 2.0 Complet
