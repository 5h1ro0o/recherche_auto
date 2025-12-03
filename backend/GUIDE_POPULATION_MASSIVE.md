# 🚀 GUIDE DE POPULATION MASSIVE DE L'ENCYCLOPÉDIE

Ce guide explique comment remplir votre base de données avec **TOUTES** les marques automobiles et des milliers de modèles.

---

## 📊 CE QUI SERA AJOUTÉ

Le script `populate_encyclopedia_massive.py` va ajouter :

✅ **100+ marques automobiles** (toutes les marques mondiales : Europe, Asie, Amérique)
- France : Renault, Peugeot, Citroën, DS, Alpine, Bugatti
- Allemagne : Volkswagen, BMW, Mercedes-Benz, Audi, Porsche, Opel
- Italie : Fiat, Ferrari, Lamborghini, Maserati, Alfa Romeo
- Royaume-Uni : Rolls-Royce, Bentley, Aston Martin, Jaguar, Land Rover, McLaren
- Japon : Toyota, Honda, Nissan, Mazda, Subaru, Lexus, Infiniti
- Corée : Hyundai, Kia, Genesis
- Chine : BYD, NIO, Xpeng, Geely, MG
- USA : Tesla, Ford, Chevrolet, Cadillac, Jeep, Rivian, Lucid
- Et bien d'autres !

✅ **1000-1500 modèles de voitures** (10-15 modèles variés par marque)
- Citadines, Berlines, SUV, Sportives, Électriques
- Avec toutes les caractéristiques techniques (dimensions, puissance, prix, etc.)

✅ **60 moteurs** variés avec spécifications complètes
- Essence atmosphérique et turbo (1.0, 1.2, 1.5, 2.0, 3.0, etc.)
- Diesel (1.5 dCi, 2.0 TDI, etc.)
- Hybride et Hybride Rechargeable
- Électrique (100-500 kW)

✅ **15 transmissions** (boîtes de vitesses)
- Manuelles (BVM5, BVM6)
- Robotisées (EDC6/7, DSG6/7, PDK7)
- Automatiques (BVA6/8/9/10)
- CVT et réducteurs électriques

✅ **400 avis clients** réalistes
- 100 avis sur les marques
- 100 avis sur les modèles
- 100 avis sur les moteurs
- 100 avis sur les transmissions

---

## 🔧 PRÉREQUIS

### 1. Base de données PostgreSQL
Vous DEVEZ avoir PostgreSQL installé et démarré :

```bash
# Vérifier si PostgreSQL est installé
psql --version

# Vérifier si PostgreSQL est démarré
# Sur Linux :
sudo systemctl status postgresql
sudo systemctl start postgresql  # Si arrêté

# Sur Windows :
# Démarrer depuis "Services" ou via pg_ctl

# Sur Mac :
brew services start postgresql
```

### 2. Base de données créée
```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer la base de données
CREATE DATABASE recherche_auto;

# Vérifier
\l
\q
```

### 3. Migrations appliquées
```bash
cd backend/

# Appliquer toutes les migrations Alembic
alembic upgrade head
```

### 4. Configuration .env
Créer le fichier `backend/.env` :

```env
DATABASE_URL=postgresql+psycopg2://postgres:votre_mot_de_passe@localhost:5432/recherche_auto
```

⚠️ **Remplacez `postgres` et `votre_mot_de_passe` par vos vrais identifiants !**

---

## ⚡ EXÉCUTION DU SCRIPT

### Méthode 1 : Exécution directe (recommandé)

```bash
cd backend/

# Exécuter le script de population massive
python populate_encyclopedia_massive.py
```

Le script va :
1. ✅ Générer 60 moteurs variés
2. ✅ Générer 15 transmissions
3. ✅ Générer 100+ marques
4. ✅ Générer 1000-1500 modèles (10-15 par marque)
5. ✅ Générer 400 avis clients

**Durée estimée : 2-5 minutes**

### Méthode 2 : En cas de problème de connexion

Si vous avez un message d'erreur de connexion PostgreSQL :

```bash
# Vérifier la connexion
python -c "from app.db import SessionLocal; db = SessionLocal(); print('✅ Connexion OK'); db.close()"
```

Si ça échoue, vérifiez :
- PostgreSQL est bien démarré
- Le fichier `.env` contient la bonne URL
- Le port 5432 est bien utilisé par PostgreSQL

---

## 🎯 VÉRIFICATION DES RÉSULTATS

### Via SQL
```bash
# Se connecter à la base
psql -U postgres -d recherche_auto

# Compter les données
SELECT 'Marques' as table_name, COUNT(*) as count FROM car_brands
UNION ALL
SELECT 'Modèles', COUNT(*) FROM car_models
UNION ALL
SELECT 'Moteurs', COUNT(*) FROM engines
UNION ALL
SELECT 'Transmissions', COUNT(*) FROM transmissions
UNION ALL
SELECT 'Avis marques', COUNT(*) FROM brand_reviews
UNION ALL
SELECT 'Avis modèles', COUNT(*) FROM model_reviews;
```

Vous devriez voir :
```
table_name      | count
----------------+-------
Marques         | 80+
Modèles         | 1000+
Moteurs         | 60
Transmissions   | 15
Avis marques    | 100
Avis modèles    | 100
```

### Via Python
```bash
python -c "
from app.db import SessionLocal
from app.models import CarBrand, CarModel, Engine, Transmission

db = SessionLocal()
print(f'📦 Marques: {db.query(CarBrand).count()}')
print(f'🚗 Modèles: {db.query(CarModel).count()}')
print(f'⚙️  Moteurs: {db.query(Engine).count()}')
print(f'🔧 Transmissions: {db.query(Transmission).count()}')
db.close()
"
```

---

## 🔄 RÉEXÉCUTION DU SCRIPT

### Nettoyer la base avant réexécution

Si vous voulez réexécuter le script pour regénérer toutes les données :

```bash
# Méthode 1 : Via SQL
psql -U postgres -d recherche_auto -c "
TRUNCATE TABLE transmission_reviews, engine_reviews, model_reviews, brand_reviews,
             engine_transmission_associations, transmission_model_associations,
             engine_model_associations, technical_specifications,
             transmissions, engines, car_models, car_brands
RESTART IDENTITY CASCADE;
"

# Méthode 2 : Recréer la base
psql -U postgres -c "DROP DATABASE recherche_auto;"
psql -U postgres -c "CREATE DATABASE recherche_auto;"
cd backend/
alembic upgrade head
```

Puis réexécuter :
```bash
python populate_encyclopedia_massive.py
```

---

## 🎨 PERSONNALISATION

### Modifier le nombre de modèles par marque

Dans `populate_encyclopedia_massive.py`, ligne ~609 :

```python
# Changer de 10-15 à vos valeurs
models = generate_models_for_brand(db, brand, engines, transmissions, count=random.randint(10, 15))
```

Par exemple, pour 20-30 modèles par marque :
```python
models = generate_models_for_brand(db, brand, engines, transmissions, count=random.randint(20, 30))
```

### Ajouter plus de moteurs

Ligne ~601 :
```python
engines = generate_engines(db, count=60)  # Changer à 100, 200, etc.
```

### Ajouter plus d'avis

Ligne ~618 :
```python
generate_reviews(db, brands, all_models, engines, transmissions, count_per_type=100)  # Changer à 200, 500, etc.
```

---

## ❓ PROBLÈMES COURANTS

### 1. "ModuleNotFoundError: No module named 'sqlalchemy'"

```bash
cd backend/
pip install -r requirements.txt
```

### 2. "psycopg2.OperationalError: connection refused"

PostgreSQL n'est pas démarré :
```bash
sudo systemctl start postgresql  # Linux
brew services start postgresql   # Mac
# Windows : Démarrer depuis Services
```

### 3. "relation does not exist"

Les migrations ne sont pas appliquées :
```bash
cd backend/
alembic upgrade head
```

### 4. "UNIQUE constraint failed"

La base contient déjà des données. Nettoyez avant :
```bash
psql -U postgres -d recherche_auto -c "TRUNCATE TABLE car_brands CASCADE;"
```

### 5. Le script est trop lent

Réduisez le nombre de modèles ou d'avis dans le script.

---

## 📚 SOURCES DES DONNÉES

Les données sont générées de manière intelligente basées sur :
- ✅ **Marques réelles** : 80+ marques automobiles mondiales existantes
- ✅ **Segments réalistes** : Citadines, Berlines, SUV adaptés à chaque marque
- ✅ **Moteurs authentiques** : Templates basés sur les motorisations réelles du marché
- ✅ **Prix cohérents** : Fourchettes de prix par segment (Low-Cost, Généraliste, Premium, Luxe)
- ✅ **Caractéristiques techniques** : Dimensions, puissances, consommations réalistes

---

## 🎉 C'EST PRÊT !

Une fois le script exécuté avec succès, votre encyclopédie automobile est **COMPLÈTE** avec :
- Toutes les marques mondiales
- Des milliers de modèles
- Tous les types de moteurs
- Toutes les transmissions
- Des centaines d'avis

Vous pouvez maintenant :
1. ✅ Démarrer votre API FastAPI : `uvicorn app.main:app --reload`
2. ✅ Accéder à l'encyclopédie via l'interface frontend
3. ✅ Consulter toutes les marques, modèles, comparaisons, etc.

🚗 **Bonne route avec votre encyclopédie automobile complète !** 🚗
