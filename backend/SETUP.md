# Configuration et Installation du Backend

## Prérequis

- Python 3.11+
- PostgreSQL 14+
- Redis (optionnel)
- Elasticsearch (optionnel)

## Installation

### 1. Créer l'environnement virtuel

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer PostgreSQL

#### Créer la base de données

```bash
# Via psql
psql -U postgres
CREATE DATABASE vehicles;
\q

# OU via createdb
createdb -U postgres vehicles
```

#### Vérifier la connexion

```bash
psql -U postgres -d vehicles -c "SELECT version();"
```

### 4. Configurer les variables d'environnement

#### Créer le fichier `.env`

Créez un fichier `.env` dans le dossier `backend/` :

```env
# Base de données PostgreSQL
DATABASE_URL=postgresql+psycopg2://postgres:votre_mot_de_passe@localhost:5432/vehicles

# Redis (optionnel)
REDIS_URL=redis://localhost:6379/0
REDIS_QUEUE_KEY=scraper_queue

# Elasticsearch (optionnel)
ELASTIC_HOST=http://localhost:9200
ES_INDEX=vehicles

# Sécurité JWT
SECRET_KEY=votre-cle-secrete-super-longue-et-aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# APIs externes (optionnelles)
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# Logs
LOG_LEVEL=INFO
```

#### Note importante sur DATABASE_URL

Si votre mot de passe PostgreSQL contient des **caractères spéciaux** (é, è, à, @, #, etc.), utilisez le script helper :

```bash
python scripts/generate_database_url.py
```

Ce script va:
1. Vous demander vos credentials PostgreSQL
2. Encoder automatiquement les caractères spéciaux
3. Générer la DATABASE_URL correcte à copier dans `.env`

### 5. Initialiser la base de données

#### Option 1: Script automatique (RECOMMANDÉ)

```bash
python scripts/init_db.py
```

Ce script va:
- ✓ Vérifier la connexion PostgreSQL
- ✓ Appliquer toutes les migrations Alembic
- ✓ Créer toutes les tables nécessaires
- ✓ Afficher la liste des tables créées

#### Option 2: Commandes manuelles

```bash
# Voir l'état actuel des migrations
alembic current

# Appliquer toutes les migrations
alembic upgrade head

# Vérifier que les tables sont créées
python -c "from app.db import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
```

### 6. Démarrer le serveur

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera accessible sur:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## Vérification de l'installation

### Tester la connexion

```bash
curl http://localhost:8000/api/health
```

### Créer un compte utilisateur

Via l'interface web ou via curl:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "motdepasse123",
    "full_name": "Test User",
    "role": "particular"
  }'
```

## Dépannage

### Erreur: "la relation « users » n'existe pas"

**Cause**: Les migrations Alembic n'ont pas été appliquées.

**Solution**:
```bash
python scripts/init_db.py
```

### Erreur: "UnicodeDecodeError: 'utf-8' codec can't decode byte"

**Cause**: Votre DATABASE_URL contient des caractères accentués non encodés.

**Solution**:
```bash
python scripts/generate_database_url.py
```

### Erreur: "connection refused" ou "could not connect to server"

**Cause**: PostgreSQL n'est pas démarré ou n'écoute pas sur le bon port.

**Solution Windows**:
1. Ouvrir "Services" (services.msc)
2. Chercher "postgresql-x64-XX"
3. Démarrer le service

**Solution Linux/Mac**:
```bash
# Vérifier le statut
sudo systemctl status postgresql

# Démarrer PostgreSQL
sudo systemctl start postgresql
```

### Erreur: "FATAL: password authentication failed"

**Cause**: Mauvais mot de passe dans DATABASE_URL

**Solution**: Vérifiez vos credentials PostgreSQL:
```bash
# Tester la connexion manuellement
psql -U postgres -d vehicles

# Si ça marche, mettez le même mot de passe dans .env
```

## Structure de la base de données

Après l'initialisation, vous aurez ces tables:

- **users**: Utilisateurs (particuliers, professionnels, admins)
- **vehicles**: Véhicules scrapés et normalisés
- **favorites**: Favoris des utilisateurs
- **alerts**: Alertes de recherche
- **alert_history**: Historique des alertes envoyées
- **messages**: Messages entre utilisateurs
- **scraper_logs**: Logs des scrapers

## Migrations Alembic

### Créer une nouvelle migration

```bash
# Auto-générer une migration basée sur les changements de modèles
alembic revision --autogenerate -m "Description des changements"

# Créer une migration vide (pour changements manuels)
alembic revision -m "Description"
```

### Appliquer/Annuler les migrations

```bash
# Appliquer toutes les migrations
alembic upgrade head

# Appliquer jusqu'à une révision spécifique
alembic upgrade <revision_id>

# Annuler la dernière migration
alembic downgrade -1

# Revenir à une révision spécifique
alembic downgrade <revision_id>

# Voir l'historique
alembic history

# Voir la révision actuelle
alembic current
```

## Variables d'environnement disponibles

| Variable | Description | Défaut |
|----------|-------------|--------|
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql+psycopg2://postgres:postgres@localhost:5432/vehicles` |
| `REDIS_URL` | URL de connexion Redis | `redis://127.0.0.1:6379/0` |
| `REDIS_QUEUE_KEY` | Clé de la queue Redis | `scraper_queue` |
| `ELASTIC_HOST` | URL Elasticsearch | `http://localhost:9200` |
| `ES_INDEX` | Nom de l'index Elasticsearch | `vehicles` |
| `SECRET_KEY` | Clé secrète JWT | (requis en production) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de vie des tokens | `1440` (24h) |
| `ANTHROPIC_API_KEY` | Clé API Anthropic (recherche IA) | (optionnel) |
| `OPENAI_API_KEY` | Clé API OpenAI (chatbot) | (optionnel) |
| `LOG_LEVEL` | Niveau de logs | `INFO` |

## Support

Pour plus d'aide:
- Documentation FastAPI: https://fastapi.tiangolo.com/
- Documentation Alembic: https://alembic.sqlalchemy.org/
- Documentation PostgreSQL: https://www.postgresql.org/docs/
