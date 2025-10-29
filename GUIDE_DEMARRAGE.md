# Guide de Démarrage - Plateforme de Recherche Automobile

Ce guide vous accompagne pas à pas pour installer et démarrer le projet complet.

## Architecture du Projet

- **Backend** : FastAPI (Python) - API REST
- **Frontend** : React + Vite
- **Base de données** : PostgreSQL 17
- **Search Engine** : Elasticsearch (optionnel pour commencer)
- **Cache/Queue** : Redis (optionnel pour commencer)
- **Worker** : Celery pour les tâches asynchrones (optionnel)

## Prérequis

### Obligatoires

- **Python 3.10+** (recommandé : 3.11 ou 3.12, éviter 3.13 si possible pour la compatibilité)
- **Node.js 18+** et npm
- **PostgreSQL 17** (ou 15+)
- **Git**

### Optionnels (pour les fonctionnalités avancées)

- **Elasticsearch 8+** (pour la recherche avancée)
- **Redis** (pour le cache et Celery)
- **MinIO** (pour le stockage d'images)

## 🚀 Installation Rapide (Mode Débutant)

### Étape 1 : Cloner le projet

```bash
git clone <url-du-repo>
cd recherche_auto
```

### Étape 2 : Configuration de PostgreSQL

#### 2.1 Créer la base de données

Ouvrez psql ou pgAdmin et exécutez :

```sql
-- Créer la base de données
CREATE DATABASE recherche_auto
    ENCODING 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252';

-- Créer l'utilisateur app (si pas déjà existant)
CREATE USER app WITH PASSWORD 'changeme';

-- Donner les droits
GRANT ALL PRIVILEGES ON DATABASE recherche_auto TO app;

-- Se connecter à la base de données
\c recherche_auto

-- Donner les droits sur le schéma public
GRANT ALL PRIVILEGES ON SCHEMA public TO app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app;
```

#### 2.2 Vérifier la connexion

```bash
cd backend
python check_db_encoding.py
```

Vous devriez voir :
```
Encodage de la base de données: UTF8
LC_COLLATE: French_France.1252
LC_CTYPE: French_France.1252
✓ Vérification terminée avec succès
```

### Étape 3 : Configuration du Backend

#### 3.1 Créer l'environnement virtuel Python

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 3.2 Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note** : Si vous rencontrez des erreurs avec Playwright sur Windows :
```bash
# Installer les navigateurs Playwright
playwright install chromium
```

#### 3.3 Configuration de l'environnement

Créer le fichier `.env` dans le dossier `backend/` :

```bash
# Windows PowerShell
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Éditer le fichier `.env` et vérifier les valeurs :

```env
DATABASE_URL=postgresql+psycopg2://app:changeme@127.0.0.1:5432/recherche_auto
SECRET_KEY=votre-cle-secrete-super-longue-et-aleatoire
LOG_LEVEL=INFO
```

**Important** : Changez `SECRET_KEY` pour quelque chose d'unique !

#### 3.4 Initialiser la base de données

```bash
# Créer les tables avec Alembic
alembic upgrade head
```

Si tout se passe bien, vous devriez voir :
```
INFO  [alembic.runtime.migration] Running upgrade -> xxx, create_vehicles
INFO  [alembic.runtime.migration] Running upgrade xxx -> yyy, add_users_roles
...
```

#### 3.5 Créer un utilisateur admin (optionnel)

Créez un script `create_admin.py` dans `backend/` :

```python
from app.db import SessionLocal
from app.models import User, UserRole
from app.auth import get_password_hash
import uuid

db = SessionLocal()

admin_user = User(
    id=str(uuid.uuid4()),
    email="admin@example.com",
    hashed_password=get_password_hash("admin123"),
    full_name="Administrateur",
    role=UserRole.ADMIN,
    is_active=True,
    is_verified=True
)

db.add(admin_user)
db.commit()
print(f"✓ Utilisateur admin créé : {admin_user.email}")
db.close()
```

Puis exécutez :
```bash
python create_admin.py
```

#### 3.6 Démarrer le serveur backend

```bash
# Mode développement avec rechargement automatique
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Vous devriez voir :
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Testez l'API : http://127.0.0.1:8000 devrait afficher `{"message": "API ok", "version": "0.2.0"}`

Documentation interactive : http://127.0.0.1:8000/docs

### Étape 4 : Configuration du Frontend

#### 4.1 Installer les dépendances

Ouvrez un **nouveau terminal** (laissez le backend tourner) :

```bash
cd frontend
npm install
```

#### 4.2 Configuration de l'environnement

```bash
# Windows PowerShell
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Le fichier `.env` devrait contenir :
```env
VITE_API_URL=http://localhost:8000
```

#### 4.3 Démarrer le serveur frontend

```bash
npm run dev
```

Vous devriez voir :
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Étape 5 : Tester l'Application

Ouvrez votre navigateur sur http://localhost:5173

#### Test 1 : Inscription

1. Allez sur la page d'inscription
2. Créez un compte avec :
   - Email : `test@example.com`
   - Mot de passe : `Test123!`
   - Nom complet : `Test User`
   - Rôle : `PARTICULAR` (Particulier)

3. Cliquez sur "S'inscrire"

#### Test 2 : Connexion

1. Allez sur la page de connexion
2. Connectez-vous avec les identifiants créés

#### Test 3 : Recherche

1. Une fois connecté, allez sur la page de recherche
2. Essayez une recherche (ex: "Peugeot 308")
3. **Note** : Les résultats seront vides car il n'y a pas encore de véhicules dans la base

## 🔧 Commandes Utiles

### Backend

```bash
# Activer l'environnement virtuel
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Démarrer le serveur
uvicorn app.main:app --reload

# Créer une nouvelle migration
alembic revision --autogenerate -m "description"

# Appliquer les migrations
alembic upgrade head

# Voir l'historique des migrations
alembic history

# Vérifier la base de données
python check_db_encoding.py
```

### Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Démarrer en mode développement
npm run dev

# Build pour la production
npm run build

# Prévisualiser le build de production
npm run preview

# Linter
npm run lint
```

## 🐛 Dépannage

### Erreur : "Base de données 'vehicles' n'existe pas"

**Solution** : Le nom de la base a été corrigé. Assurez-vous que votre `.env` pointe vers `recherche_auto` :
```env
DATABASE_URL=postgresql+psycopg2://app:changeme@127.0.0.1:5432/recherche_auto
```

### Erreur : "UnicodeDecodeError" avec psycopg2

**Solution** : Utilisez le script `check_db_encoding.py` qui contourne ce problème.

### Erreur : "Module 'app' not found"

**Solution** : Assurez-vous d'être dans le dossier `backend/` et que l'environnement virtuel est activé.

### Le frontend ne se connecte pas au backend

**Solution** :
1. Vérifiez que le backend tourne sur http://localhost:8000
2. Vérifiez le fichier `frontend/.env` : `VITE_API_URL=http://localhost:8000`
3. Redémarrez le serveur frontend après modification du `.env`

### Erreurs CORS

**Solution** : Le backend est configuré pour accepter `localhost:5173`. Si vous utilisez un autre port, modifiez `backend/.env` :
```env
ALLOW_ORIGINS=http://localhost:5173,http://localhost:VOTRE_PORT
```

## 📦 Fonctionnalités Avancées (Optionnel)

### Installation d'Elasticsearch

Pour activer la recherche avancée :

```bash
# Télécharger Elasticsearch 8.x depuis elastic.co
# Démarrer Elasticsearch
# Par défaut sur http://localhost:9200

# Vérifier dans backend/.env :
ELASTIC_HOST=http://localhost:9200
ES_INDEX=vehicles
```

### Installation de Redis

Pour le cache et Celery :

```bash
# Windows : Télécharger Redis depuis GitHub (tporadowski/redis)
# Linux : sudo apt install redis-server
# Mac : brew install redis

# Démarrer Redis
redis-server

# Vérifier dans backend/.env :
REDIS_URL=redis://127.0.0.1:6379/0
```

### Démarrer Celery Worker

Pour les tâches asynchrones (scraping, etc.) :

```bash
cd backend

# Windows
celery -A app.celery_app worker --loglevel=info --pool=solo

# Linux/Mac
celery -A app.celery_app worker --loglevel=info
```

### Démarrer Flower (Monitoring Celery)

```bash
celery -A app.celery_app flower --port=5555
```

Accédez à http://localhost:5555

## 🎯 Prochaines Étapes

1. **Ajouter des véhicules de test** : Utilisez l'API `/api/admin/vehicles` pour ajouter des véhicules
2. **Configurer le scraping** : Consultez `backend/scrapers/` pour automatiser la collecte de données
3. **Personnaliser le frontend** : Modifiez les composants dans `frontend/src/components/`
4. **Configurer l'authentification par email** : Intégrez un service d'envoi d'emails

## 📚 Documentation Supplémentaire

- **API Documentation** : http://localhost:8000/docs (Swagger)
- **API Redoc** : http://localhost:8000/redoc
- **Frontend Components** : Voir `frontend/src/components/`
- **Backend Routes** : Voir `backend/app/routes/`

## 🆘 Besoin d'Aide ?

- Consultez les logs du backend dans le terminal
- Consultez les logs du frontend dans la console du navigateur (F12)
- Vérifiez les issues GitHub du projet

## ✅ Checklist de Démarrage

- [ ] PostgreSQL 17 installé et configuré
- [ ] Base de données `recherche_auto` créée
- [ ] Utilisateur `app` avec mot de passe `changeme` créé
- [ ] Python 3.10+ installé
- [ ] Node.js 18+ installé
- [ ] Backend : environnement virtuel créé et activé
- [ ] Backend : dépendances installées (`pip install -r requirements.txt`)
- [ ] Backend : fichier `.env` configuré
- [ ] Backend : migrations appliquées (`alembic upgrade head`)
- [ ] Backend : serveur démarré (http://localhost:8000)
- [ ] Frontend : dépendances installées (`npm install`)
- [ ] Frontend : fichier `.env` configuré
- [ ] Frontend : serveur démarré (http://localhost:5173)
- [ ] Test d'inscription effectué
- [ ] Test de connexion effectué

Bon développement ! 🚗💨
