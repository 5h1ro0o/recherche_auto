# 📖 GUIDE COMPLET DE MISE EN PLACE DE L'ENCYCLOPÉDIE AUTOMOBILE

Ce guide explique **étape par étape** comment mettre en place tout le système d'encyclopédie automobile avec scraping automatique depuis Internet.

---

## 🎯 VUE D'ENSEMBLE

Le système collecte automatiquement depuis Internet :
- ✅ **TOUTES les marques automobiles** (100-200 marques mondiales)
- ✅ **TOUS les modèles** pour chaque marque (2000-5000+ modèles)
- ✅ **TOUS les moteurs** avec specs complètes (100-200 moteurs)
- ✅ **TOUTES les transmissions** avec fiabilité (30-50 boîtes)
- ✅ **TOUS les avis réels** (avantages/inconvénients depuis forums)

### Relations dans la base de données :
- 🔗 **Marque** ↔ **Modèles** (une marque a plusieurs modèles)
- 🔗 **Modèle** ↔ **Moteurs** (un modèle peut avoir plusieurs moteurs)
- 🔗 **Modèle** ↔ **Transmissions** (un modèle peut avoir plusieurs boîtes)
- 🔗 **Moteur** ↔ **Transmissions** (quelles boîtes vont avec quel moteur)

---

## 📋 PRÉREQUIS

### Système
- **PostgreSQL** installé et démarré
- **Python 3.9+** installé
- **Node.js 18+** installé (pour le frontend)
- **Git** installé

### Vérifier PostgreSQL
```bash
# Windows
pg_ctl status

# Linux/Mac
sudo systemctl status postgresql
```

---

## 🚀 INSTALLATION ÉTAPE PAR ÉTAPE

### ÉTAPE 1 : Cloner le projet et installer les dépendances

```bash
# Cloner le projet (si pas déjà fait)
cd /chemin/vers/recherche_auto

# Backend - Installer les dépendances Python
cd backend
pip install -r requirements.txt

# Frontend - Installer les dépendances Node
cd ../frontend
npm install
```

### ÉTAPE 2 : Configuration de la base de données

```bash
# Retour au backend
cd ../backend

# Créer le fichier .env s'il n'existe pas
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost:5432/recherche_auto
EOF
```

⚠️ **IMPORTANT** : Remplace `user`, `password` et `recherche_auto` par tes vraies valeurs !

### ÉTAPE 3 : Créer la base de données

```bash
# Connexion à PostgreSQL
psql -U postgres

# Dans psql :
CREATE DATABASE recherche_auto;
\q
```

### ÉTAPE 4 : Appliquer les migrations Alembic

```bash
# Depuis le dossier backend/

# Vérifier les migrations disponibles
alembic history

# Appliquer TOUTES les migrations
alembic upgrade head
```

Tu devrais voir :
```
INFO  [alembic.runtime.migration] Running upgrade  -> df5ee69f89fe, initial
INFO  [alembic.runtime.migration] Running upgrade df5ee69f89fe -> a1b2c3d4e5f6, add car encyclopedia tables
INFO  [alembic.runtime.migration] Running upgrade a1b2c3d4e5f6 -> b1c2d3e4f5g6, add encyclopedia relations tables
```

✅ **Vérification** : Ta base de données a maintenant TOUTES les tables !

### ÉTAPE 5 : Vérifier les tables créées

```bash
# Connexion à la base
psql -U user -d recherche_auto

# Lister les tables
\dt

# Tu devrais voir :
# car_brands
# car_models
# engines
# transmissions
# engine_model_associations
# transmission_model_associations
# engine_transmission_associations
# technical_specifications
# brand_reviews
# model_reviews
# engine_reviews
# transmission_reviews

\q
```

---

## 🌐 COLLECTE DES DONNÉES DEPUIS INTERNET

### MÉTHODE 1 : Scraper COMPLET (RECOMMANDÉ)

Ce script collecte **TOUT** automatiquement :

```bash
cd backend

# Lancer le scraper complet
python scrape_complete_encyclopedia.py
```

Ce script va :
1. ✅ Collecter TOUTES les marques depuis Wikipedia, Automobile-Catalog, CarLogos
2. ✅ Pour chaque marque : historique, réputation, avis
3. ✅ Pour chaque marque : TOUS les modèles
4. ✅ Pour chaque modèle : TOUTES les caractéristiques techniques
5. ✅ Pour chaque modèle : TOUS les avis Caradisiac et forums
6. ✅ Sauvegarder automatiquement dans la base

⏱️ **Temps estimé** : 10-15 heures (tu peux le laisser tourner toute la nuit)

### MÉTHODE 2 : Scrapers séparés (par catégorie)

Si tu veux lancer les scrapers séparément :

```bash
# 1. Modèles avec caractéristiques et avis
python scrape_models_web.py

# 2. Moteurs avec specs et fiabilité
python scrape_engines_web.py

# 3. Transmissions avec fiabilité
python scrape_transmissions_web.py
```

### MÉTHODE 3 : Script orchestrateur

```bash
# Lance tous les scrapers en séquence avec statistiques
python run_all_scrapers.py
```

---

## 🔗 CRÉER LES LIENS ENTRE LES DONNÉES

Après la collecte, il faut créer les associations entre moteurs, modèles et transmissions.

### Script de liaison (à créer)

```bash
cd backend
python link_engines_models_transmissions.py
```

Ce script va :
1. Analyser les données collectées
2. Créer les liens moteur ↔ modèle
3. Créer les liens transmission ↔ modèle
4. Créer les liens moteur ↔ transmission

---

## 📊 VÉRIFIER LES DONNÉES

```bash
# Connexion à la base
psql -U user -d recherche_auto

# Compter les marques
SELECT COUNT(*) FROM car_brands;

# Compter les modèles
SELECT COUNT(*) FROM car_models;

# Compter les moteurs
SELECT COUNT(*) FROM engines;

# Compter les transmissions
SELECT COUNT(*) FROM transmissions;

# Vérifier les liens moteur-modèle
SELECT COUNT(*) FROM engine_model_associations;

# Voir quels moteurs pour un modèle spécifique
SELECT e.name, e.power_hp, e.fuel_type
FROM engines e
JOIN engine_model_associations ema ON e.id = ema.engine_id
JOIN car_models cm ON ema.model_id = cm.id
WHERE cm.name = 'Clio V';

# Voir dans quels modèles un moteur est équipé
SELECT cm.name, cb.name as brand
FROM car_models cm
JOIN car_brands cb ON cm.brand_id = cb.id
JOIN engine_model_associations ema ON cm.id = ema.model_id
JOIN engines e ON ema.engine_id = e.id
WHERE e.name = 'TCe 130';

\q
```

---

## 🚀 DÉMARRER L'APPLICATION

### Backend (API)

```bash
cd backend

# Démarrer FastAPI
uvicorn app.main:app --reload --port 8000
```

L'API sera accessible sur : `http://localhost:8000`

### Frontend (React)

```bash
cd frontend

# Démarrer le serveur de développement
npm run dev
```

Le frontend sera accessible sur : `http://localhost:5173`

---

## 🔍 UTILISER L'ENCYCLOPÉDIE

### Via l'interface web

1. Ouvre `http://localhost:5173`
2. Va sur la page "Encyclopédie"
3. Explore :
   - 🚗 **Marques** : Liste complète avec réputation
   - 🚘 **Modèles** : Filtres par marque, segment, prix
   - 🔧 **Moteurs** : Filtres par type, puissance, fiabilité
   - ⚙️ **Transmissions** : Filtres par type, fiabilité

### Via l'API

```bash
# Toutes les marques
curl http://localhost:8000/encyclopedia/brands

# Tous les modèles d'une marque
curl http://localhost:8000/encyclopedia/models?brand_id=renault-id

# Détails d'un modèle avec ses moteurs et transmissions
curl http://localhost:8000/encyclopedia/models/clio-v-id

# Tous les modèles équipés d'un moteur
curl http://localhost:8000/encyclopedia/engines/tce-130-id/models

# Toutes les transmissions pour un moteur
curl http://localhost:8000/encyclopedia/engines/tce-130-id/transmissions
```

---

## 📈 EXEMPLES DE REQUÊTES UTILES

### Trouver tous les modèles avec un moteur spécifique

```python
# Dans un script Python
from app.models import Engine, CarModel
from app.database import SessionLocal

db = SessionLocal()

# Récupérer le moteur TCe 130
engine = db.query(Engine).filter(Engine.name == "TCe 130").first()

# Tous les modèles équipés de ce moteur
if engine:
    models = engine.models  # Grâce à la relation many-to-many !
    for model in models:
        print(f"- {model.brand.name} {model.name}")
```

### Trouver toutes les transmissions pour un modèle

```python
# Récupérer un modèle
model = db.query(CarModel).filter(CarModel.name == "Clio V").first()

# Toutes les transmissions disponibles
if model:
    transmissions = model.transmissions
    for trans in transmissions:
        print(f"- {trans.name} ({trans.type})")
```

### Trouver les combinaisons moteur-boîte

```python
# Récupérer un moteur
engine = db.query(Engine).filter(Engine.name == "TDI 150").first()

# Toutes les boîtes compatibles
if engine:
    transmissions = engine.transmissions
    for trans in transmissions:
        print(f"- {trans.name}")
```

---

## ⚠️ DÉPANNAGE

### Problème : "Relation does not exist"

```bash
# Réappliquer les migrations
cd backend
alembic downgrade base
alembic upgrade head
```

### Problème : "Could not connect to database"

```bash
# Vérifier que PostgreSQL est démarré
# Windows
pg_ctl status

# Linux
sudo systemctl status postgresql

# Démarrer PostgreSQL si nécessaire
sudo systemctl start postgresql
```

### Problème : "No module named 'app'"

```bash
# S'assurer d'être dans le dossier backend/
cd backend

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Problème : Scraping bloqué

- Certains sites peuvent bloquer après trop de requêtes
- Le script respecte des délais (2-3 secondes entre requêtes)
- Si bloqué : attendre 1 heure et relancer

---

## 📝 MISE À JOUR DES DONNÉES

Pour mettre à jour l'encyclopédie avec de nouvelles données :

```bash
# Relancer le scraper complet
python scrape_complete_encyclopedia.py

# Ou scrapers individuels
python scrape_models_web.py
python scrape_engines_web.py
python scrape_transmissions_web.py
```

Les données existantes seront mises à jour ou complétées.

---

## 🎉 RÉSULTAT FINAL

Après avoir suivi ce guide, tu auras :

✅ Une base de données complète avec :
   - 100-200 marques automobiles
   - 2000-5000+ modèles
   - 100-200 moteurs
   - 30-50 transmissions
   - TOUS les liens entre eux

✅ Toutes les caractéristiques techniques de chaque modèle

✅ Tous les avis réels (avantages/inconvénients)

✅ Une API REST complète pour interroger les données

✅ Une interface web pour explorer l'encyclopédie

✅ La possibilité de savoir :
   - Quels moteurs équipent un modèle
   - Dans quels modèles un moteur est utilisé
   - Quelles transmissions vont avec un moteur
   - Tous les avis sur n'importe quel élément

---

## 🆘 SUPPORT

En cas de problème :

1. Vérifier les logs de l'API : `backend/logs/`
2. Vérifier la console du scraper pour les erreurs
3. Vérifier que PostgreSQL est bien démarré
4. Vérifier que toutes les migrations sont appliquées : `alembic current`

---

## 📚 DOCUMENTATION SUPPLÉMENTAIRE

- **API** : `http://localhost:8000/docs` (Swagger UI automatique)
- **Scraping** : Voir `backend/SCRAPING_README.md`
- **Relations** : Voir `backend/app/models.py`

---

**🎯 TU ES PRÊT ! Lance le scraper et laisse-le collecter toutes les données !**
