# 🚀 RÉFÉRENCE RAPIDE - SCRIPTS DE SCRAPING

## ⚡ QUEL SCRIPT UTILISER ?

### Pour commencer (RECOMMANDÉ) 👈
```bash
python scrape_all.py
```
**OU**
```bash
python scrape_encyclopedia_improved.py
```

✅ Ces scripts sont **testés, fonctionnels et sans erreurs**
✅ Collectent 57 marques + 155 modèles
✅ Temps : 2-5 minutes

---

## 📋 LISTE COMPLÈTE DES SCRIPTS

| Script | Description | Status | Durée |
|--------|-------------|--------|-------|
| `scrape_all.py` | **🌟 MASTER** - Lance tout | ✅ Testé | 5 min |
| `scrape_encyclopedia_improved.py` | **Marques + Modèles** | ✅ Testé | 3 min |
| `scrape_models_web.py` | Modèles détaillés (web) | ⚠️ Peut avoir 403 | 1-2h |
| `scrape_engines_web.py` | Moteurs | ⚠️ À tester | 30-60 min |
| `scrape_transmissions_web.py` | Transmissions | ⚠️ À tester | 30-60 min |
| `run_all_scrapers.py` | Ancien orchestrateur | ⚠️ Nécessite MAJ | 2-4h |

---

## 🎯 COMMANDES RAPIDES

### 1. Premier lancement (setup complet)
```bash
# Créer la base de données
psql -U postgres
CREATE DATABASE recherche_auto;
\q

# Appliquer les migrations
cd backend
alembic upgrade head

# Lancer le scraping
python scrape_all.py
```

### 2. Juste collecter les données
```bash
cd backend
python scrape_encyclopedia_improved.py
```

### 3. Vérifier les résultats
```bash
psql -U postgres -d recherche_auto

SELECT COUNT(*) FROM car_brands;     -- Devrait afficher 57
SELECT COUNT(*) FROM car_models;     -- Devrait afficher 155

SELECT cb.name, COUNT(cm.id) as nb_modeles
FROM car_brands cb
LEFT JOIN car_models cm ON cb.id = cm.brand_id
GROUP BY cb.name
ORDER BY nb_modeles DESC;

\q
```

### 4. Démarrer l'application
```bash
# Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend (nouveau terminal)
cd frontend
npm run dev
```

---

## 📊 RÉSULTATS ATTENDUS

Après `python scrape_all.py` :

```
✅ 57 marques automobiles
   • 🇫🇷 Françaises : Renault, Peugeot, Citroën, Dacia, etc.
   • 🇩🇪 Allemandes : Volkswagen, BMW, Mercedes-Benz, Audi, etc.
   • 🇯🇵 Japonaises : Toyota, Honda, Nissan, Mazda, etc.
   • 🇰🇷 Coréennes : Hyundai, Kia, Genesis, etc.
   • 🇺🇸 Américaines : Tesla, Ford, Chevrolet, etc.
   • Et 40+ autres marques mondiales

✅ 155 modèles de voitures
   • Renault : Clio, Captur, Megane, etc. (9 modèles)
   • Peugeot : 208, 2008, 308, 3008, etc. (8 modèles)
   • Volkswagen : Polo, Golf, Tiguan, etc. (11 modèles)
   • BMW : Série 1, 3, 5, X1, X3, etc. (12 modèles)
   • Et bien d'autres...
```

---

## 🔧 EN CAS DE PROBLÈME

### PostgreSQL ne démarre pas
```bash
# Windows
pg_ctl start -D "C:\Program Files\PostgreSQL\15\data"

# Linux/Mac
sudo systemctl start postgresql
```

### Erreur "Module not found"
```bash
pip install -r requirements.txt
pip install asyncpg playwright
playwright install chromium
```

### Erreur "Database does not exist"
```bash
psql -U postgres
CREATE DATABASE recherche_auto;
\q

alembic upgrade head
```

### Voir les logs détaillés
Ouvrir le script Python et modifier :
```python
engine = create_async_engine(DATABASE_URL, echo=True)  # Active les logs SQL
```

---

## 📚 DOCUMENTATION COMPLÈTE

- **Guide détaillé** : Voir `GUIDE_SCRAPERS.md`
- **Guide installation** : Voir `GUIDE_INSTALLATION_ENCYCLOPEDIE.md`
- **Documentation scraping** : Voir `SCRAPING_README.md`

---

## ✅ CHECKLIST DE VÉRIFICATION

Avant de lancer un scraper :

- [ ] PostgreSQL est démarré
- [ ] Base de données `recherche_auto` créée
- [ ] Migrations Alembic appliquées (`alembic upgrade head`)
- [ ] Fichier `.env` existe avec `DATABASE_URL`
- [ ] Dépendances Python installées (`pip install -r requirements.txt`)
- [ ] Playwright installé (`playwright install chromium`)

---

**🎯 CONSEIL** : Commencez toujours par `python scrape_all.py` - c'est le plus simple et le plus fiable !
