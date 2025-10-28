# 🚀 Guide de démarrage rapide - Recherche Auto

Ce guide vous aidera à résoudre les problèmes courants et à démarrer l'application correctement.

## 🔴 Problèmes identifiés et solutions

### 1. Incompatibilité Elasticsearch

**Problème**:
```
BadRequestError: Accept version must be either version 8 or 7, but found 9
```

**Cause**: Le client Python Elasticsearch 9.x essaie de communiquer avec un serveur Elasticsearch 8.x

**Solution**:
```bash
# Dans le dossier backend
pip install "elasticsearch>=8.0.0,<9.0.0"
```

Le fichier `requirements.txt` a été corrigé pour éviter ce problème.

### 2. Aucune donnée dans la base

**Problème**: Aucun résultat de recherche car la base Elasticsearch est vide

**Cause**: Les scrapers n'ont pas été lancés et l'index est vide

**Solution**: Utiliser le script d'initialisation (voir section suivante)

### 3. Email invalide lors de l'inscription

**Problème**:
```
value is not a valid email address: aa@aa
```

**Solution**: Utiliser un email valide avec un domaine complet:
- ✅ Valide: `test@test.com`, `user@example.fr`
- ❌ Invalide: `aa@aa`, `test@test`

## 📋 Prérequis

1. **Docker Desktop** installé et démarré
2. **Python 3.10+** installé
3. **Node.js 18+** et npm installés

## 🎯 Démarrage en 5 étapes

### Étape 1: Démarrer l'infrastructure

```bash
cd infra
docker-compose up -d
```

Services démarrés:
- 🐘 PostgreSQL (port 5432)
- 🔍 Elasticsearch (port 9200)
- 🔴 Redis (port 6379)

Vérifier que tout fonctionne:
```bash
docker-compose ps
```

Tous les services doivent être "Up" ou "healthy".

### Étape 2: Installer les dépendances Python

```bash
cd ../backend

# Créer un environnement virtuel (si pas déjà fait)
python -m venv .venv

# Activer l'environnement virtuel
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Étape 3: Initialiser la base de données

```bash
# Toujours dans le dossier backend avec l'env virtuel activé
python init_db.py
```

Ce script va:
- ✅ Vérifier la connexion à Elasticsearch
- ✅ Créer l'index "vehicles"
- ✅ Ajouter 10 véhicules de test
- ✅ Afficher des exemples de recherche

**Sortie attendue**:
```
🚀 Initialisation de la base de données...
✅ Connexion à Elasticsearch réussie
📊 Vérification de l'index 'vehicles'...
✅ Index 'vehicles' créé avec succès
📝 Indexation de 10 véhicules de test...
✅ 10/10 véhicules indexés avec succès!
```

### Étape 4: Démarrer le backend

```bash
# Dans le dossier backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le backend sera accessible sur: http://localhost:8000
Documentation API: http://localhost:8000/docs

### Étape 5: Démarrer le frontend

```bash
# Nouveau terminal, dans le dossier frontend
cd ../frontend

# Installer les dépendances (si pas déjà fait)
npm install

# Démarrer le serveur de développement
npm run dev
```

Le frontend sera accessible sur: http://localhost:5173

## ✅ Tester l'application

### 1. Créer un compte

1. Aller sur http://localhost:5173/register
2. Remplir le formulaire avec un **email valide**:
   - Email: `test@test.com`
   - Mot de passe: `password123`
   - Nom: `Test User`
3. Cliquer sur "S'inscrire"

### 2. Se connecter

1. Aller sur http://localhost:5173/login
2. Utiliser les identifiants créés
3. Vous serez redirigé vers la page de recherche

### 3. Faire une recherche

1. Sur la page d'accueil
2. Chercher: `Peugeot` ou `BMW` ou `Diesel`
3. Vous devriez voir les véhicules de test

**Exemple de recherches**:
- `Peugeot` → 1 résultat (Peugeot 208)
- `Diesel` → 4 résultats (tous les diesels)
- `automatique` → 4 résultats (boîtes auto)
- Prix max 15000€ → 5 résultats

## 🔧 Lancer les scrapers réels

Les scrapers permettent de récupérer de vraies annonces depuis:
- 🟡 LeBonCoin
- 🔵 LaCentrale
- 🟢 AutoScout24

**⚠️ Attention**: Le scraping peut être détecté et bloqué par les sites cibles.

### Option 1: Lancer un scraper manuellement

```bash
cd backend
python -m scrapers.leboncoin_scraper --query "peugeot 208" --max-pages 2
```

### Option 2: Lancer tous les scrapers avec Celery

```bash
# Terminal 1: Lancer Redis (si pas déjà fait)
cd infra
docker-compose up redis

# Terminal 2: Lancer le worker Celery
cd backend
celery -A app.worker worker --loglevel=info

# Terminal 3: Lancer Flower (monitoring)
cd backend
celery -A app.worker flower
```

Accéder à Flower: http://localhost:5555

## 🐛 Dépannage

### Problème: Elasticsearch refuse les connexions

**Symptôme**: `Connection refused` ou `Connection timeout`

**Solution**:
```bash
# Vérifier qu'Elasticsearch tourne
docker ps | grep elasticsearch

# Si absent, le démarrer
cd infra
docker-compose up -d elasticsearch

# Attendre 30 secondes puis tester
curl http://localhost:9200
```

### Problème: Le frontend ne se connecte pas au backend

**Symptôme**: Erreurs CORS ou `Network Error`

**Solutions**:
1. Vérifier que le backend tourne sur le port 8000
2. Vérifier les variables d'environnement frontend
3. Vérifier le fichier `frontend/.env`:
   ```
   VITE_API_URL=http://localhost:8000
   ```

### Problème: "Module not found" en Python

**Solution**:
```bash
# Vérifier que l'env virtuel est activé
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Réinstaller les dépendances
pip install -r requirements.txt --upgrade
```

### Problème: Erreurs de build frontend

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 📊 Vérifier que tout fonctionne

### Checklist rapide:

- [ ] Docker Desktop est lancé
- [ ] `docker ps` montre postgres, elasticsearch, redis "Up"
- [ ] `curl http://localhost:9200` retourne des infos Elasticsearch
- [ ] Backend accessible: http://localhost:8000/docs
- [ ] Frontend accessible: http://localhost:5173
- [ ] L'index contient des données: `python init_db.py` (ou vérifier avec une recherche)

### Test complet:

```bash
# 1. Tester Elasticsearch
curl http://localhost:9200/vehicles/_count

# Réponse attendue: {"count":10,...}

# 2. Tester l'API backend
curl http://localhost:8000/api/search?q=peugeot

# 3. Tester le frontend
# Ouvrir http://localhost:5173 et chercher "peugeot"
```

## 🚀 Commandes utiles

```bash
# Redémarrer tous les services Docker
cd infra
docker-compose restart

# Voir les logs Elasticsearch
docker-compose logs -f elasticsearch

# Voir les logs du backend
# (Depuis le terminal où uvicorn tourne)

# Réinitialiser complètement la base de données
cd backend
python init_db.py  # Répondre 'y' pour recréer l'index

# Nettoyer complètement et repartir de zéro
cd infra
docker-compose down -v  # ⚠️ SUPPRIME TOUTES LES DONNÉES
docker-compose up -d
cd ../backend
python init_db.py
```

## 📚 Documentation supplémentaire

- **API Backend**: http://localhost:8000/docs (Swagger UI)
- **Elasticsearch**: http://localhost:9200/_cat/indices?v
- **Celery Flower**: http://localhost:5555

## 🎉 C'est tout!

Votre application devrait maintenant fonctionner correctement avec:
- ✅ Elasticsearch compatible
- ✅ Données de test chargées
- ✅ Backend et frontend opérationnels
- ✅ Recherche fonctionnelle

Pour toute question, vérifiez les logs ou relancez l'initialisation.
