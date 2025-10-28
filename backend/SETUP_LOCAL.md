# 🚀 Configuration Locale (sans Docker)

Guide rapide pour configurer le backend en local avec PostgreSQL 17.

## ⚡ Configuration automatique (Recommandé)

**Une seule commande pour tout configurer :**

```powershell
cd C:\Users\matte\Desktop\recherche_auto\backend
.\setup.ps1
```

Ce script va :
- ✅ Créer l'environnement virtuel Python si nécessaire
- ✅ Installer toutes les dépendances
- ✅ Configurer PostgreSQL (base de données + utilisateur)
- ✅ Créer le fichier `.env` automatiquement
- ✅ Tester la connexion à PostgreSQL
- ✅ Exécuter les migrations Alembic
- ✅ Démarrer le serveur backend

**C'est tout ! 🎉**

---

## 📋 Prérequis

- ✅ PostgreSQL 17 installé
- ✅ Python 3.11+ installé
- ✅ Le service PostgreSQL démarré

### Vérifier que PostgreSQL est démarré

```powershell
# Voir le statut
Get-Service -Name postgresql*

# Si arrêté, démarrer
Start-Service postgresql-x64-17
```

---

## 🔧 Configuration manuelle (Alternative)

Si vous préférez configurer manuellement :

### 1. Créer la base de données

```powershell
.\init_database.ps1
```

Vous devrez entrer le mot de passe de l'utilisateur `postgres`.

### 2. Installer les dépendances

```powershell
# Activer l'environnement virtuel
.\.venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Tester la connexion

```powershell
python test_db_connection.py
```

### 4. Exécuter les migrations

```powershell
alembic upgrade head
```

### 5. Lancer le serveur

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🌐 Accès

- **API Backend** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **API Alternative** : http://localhost:8000/redoc

---

## 🐛 Dépannage

### Erreur "Connection refused"

PostgreSQL n'est pas démarré :
```powershell
Start-Service postgresql-x64-17
```

### Erreur "password authentication failed"

Le mot de passe dans `.env` est incorrect. Modifiez le fichier `.env` :
```env
DATABASE_URL=postgresql+psycopg2://app:VOTRE_MOT_DE_PASSE@localhost:5432/recherche_auto
```

### Erreur "database does not exist"

Relancez le script d'initialisation :
```powershell
.\init_database.ps1
```

### Tester la connexion

```powershell
python test_db_connection.py
```

---

## 📝 Configuration

Le fichier `.env` contient toute la configuration :

```env
# Base de données
DATABASE_URL=postgresql+psycopg2://app:changeme@localhost:5432/recherche_auto

# Elasticsearch (optionnel)
ELASTIC_HOST=http://localhost:9200

# Redis (optionnel)
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=votre-clé-secrète
```

---

## 🎯 Prochaines étapes

1. ✅ Backend configuré et démarré sur http://localhost:8000
2. 🚀 Lancer le frontend : `cd ../frontend && npm run dev`
3. 🌐 Accéder à l'application : http://localhost:5173

---

## 💡 Commandes utiles

```powershell
# Créer une nouvelle migration
alembic revision --autogenerate -m "description"

# Voir l'historique des migrations
alembic history

# Revenir à une migration précédente
alembic downgrade -1

# Voir les logs PostgreSQL
# Aller dans C:\Program Files\PostgreSQL\17\data\log\
```
