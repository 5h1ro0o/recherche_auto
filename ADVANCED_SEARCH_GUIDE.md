# 🔍 Guide de Recherche Avancée Multi-Sources

## Vue d'ensemble

Le système de recherche avancée permet de combiner automatiquement les résultats de **LeBonCoin** et **AutoScout24** avec des filtres stricts (pas de recherche par texte libre).

## 🎯 Caractéristiques

### ✅ Filtres disponibles

**Filtres principaux:**
- **Marque** (obligatoire) : Volkswagen, Peugeot, Renault, BMW, Audi, Mercedes, etc.
- **Modèle** (optionnel) : Golf, 308, Clio, Série 3, A4, Classe C, etc.

**Filtres de prix:**
- Prix minimum (€)
- Prix maximum (€)

**Filtres d'année:**
- Année minimum (1990-2025)
- Année maximum (1990-2025)

**Filtres de kilométrage:**
- Kilométrage minimum (km)
- Kilométrage maximum (km)

**Filtres techniques:**
- **Carburant** : Essence, Diesel, Électrique, Hybride, GPL
- **Transmission** : Manuelle, Automatique

**Sources:**
- LeBonCoin (🟠)
- AutoScout24 (🔵)
- Les deux sources sont recherchées en parallèle

## 🚀 Comment utiliser

### 1. Backend (API)

**Démarrer le serveur:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API Endpoint:**
```
POST /api/search-advanced/search
```

**Exemple de requête:**
```json
{
  "make": "volkswagen",
  "model": "golf",
  "year_min": 2015,
  "year_max": 2023,
  "price_min": 10000,
  "price_max": 25000,
  "mileage_max": 100000,
  "fuel_type": "diesel",
  "transmission": "manuelle",
  "sources": ["leboncoin", "autoscout24"],
  "max_pages": 3
}
```

**Exemple de réponse:**
```json
{
  "success": true,
  "total_results": 45,
  "results": [
    {
      "source_ids": {"autoscout24": "abc123"},
      "title": "Volkswagen Golf GTD",
      "make": "Volkswagen",
      "model": "Golf",
      "price": 18500,
      "year": 2019,
      "mileage": 75000,
      "fuel_type": "Diesel",
      "transmission": "Manuelle",
      "location_city": "Paris",
      "url": "https://...",
      "images": ["https://..."]
    }
  ],
  "sources_stats": {
    "leboncoin": {"count": 25, "success": true},
    "autoscout24": {"count": 20, "success": true}
  },
  "duration": 15.3,
  "timestamp": "2025-11-21T20:00:00"
}
```

### 2. Frontend (Interface)

**Accéder à la recherche:**
```
http://localhost:5173/
```

La page d'accueil affiche maintenant le formulaire de recherche avancée.

**Workflow:**
1. Sélectionner une **marque** (obligatoire)
2. Optionnellement sélectionner un **modèle**
3. Définir les filtres souhaités (prix, année, kilométrage, carburant, transmission)
4. Choisir les sources (LeBonCoin et/ou AutoScout24)
5. Cliquer sur **"🔍 Rechercher"**

**Résultats:**
- Les annonces des deux sources sont combinées et triées par prix
- Chaque annonce affiche la source (badge LeBonCoin ou AutoScout24)
- Statistiques de recherche en haut (nombre d'annonces par source, durée)
- Filtres appliqués affichés en tags

## 📝 Exemples d'utilisation

### Exemple 1: Rechercher toutes les Volkswagen Golf diesel

```bash
curl -X POST "http://localhost:8000/api/search-advanced/search" \
  -H "Content-Type: application/json" \
  -d '{
    "make": "volkswagen",
    "model": "golf",
    "fuel_type": "diesel",
    "sources": ["leboncoin", "autoscout24"]
  }'
```

### Exemple 2: Rechercher des BMW récentes à moins de 30000€

```bash
curl -X POST "http://localhost:8000/api/search-advanced/search" \
  -H "Content-Type: application/json" \
  -d '{
    "make": "bmw",
    "year_min": 2018,
    "price_max": 30000,
    "sources": ["leboncoin", "autoscout24"]
  }'
```

### Exemple 3: Rechercher des voitures électriques Renault

```bash
curl -X POST "http://localhost:8000/api/search-advanced/search" \
  -H "Content-Type: application/json" \
  -d '{
    "make": "renault",
    "fuel_type": "electrique",
    "sources": ["leboncoin", "autoscout24"]
  }'
```

## 🔧 Architecture

### Backend
```
backend/app/routes/search_advanced.py
├── POST /search                    # Recherche multi-sources
├── GET  /filters/makes            # Liste des marques
├── GET  /filters/models/{make}    # Liste des modèles par marque
└── GET  /filters/years            # Liste des années
```

### Frontend
```
frontend/src/
├── components/AdvancedSearchForm.jsx    # Formulaire de recherche
├── Pages/AdvancedSearchPage.jsx         # Page principale
└── ui/Results.jsx                        # Affichage des résultats
```

### Scrapers
```
backend/scrapers/
├── base_scraper.py           # Classe de base
├── leboncoin_scraper.py      # Scraper LeBonCoin
└── autoscoot_scraper.py      # Scraper AutoScout24
```

## ⚡ Performance

- **Scraping parallèle** : Les deux sources sont scrapées en même temps
- **Timeout** : 2 minutes max par source
- **Filtrage post-scraping** : Certains filtres non supportés nativement sont appliqués après
- **Tri automatique** : Résultats triés par prix croissant

## 🎨 Fonctionnalités UI

### Formulaire de recherche
- ✅ Sélection de marque avec liste déroulante
- ✅ Sélection de modèle dynamique (se charge selon la marque)
- ✅ Ranges de prix et année avec min/max
- ✅ Sélection de carburant et transmission
- ✅ Choix des sources (checkboxes)
- ✅ Bouton de réinitialisation

### Affichage des résultats
- ✅ Statistiques de recherche (nombre total, durée)
- ✅ Stats par source (LeBonCoin, AutoScout24)
- ✅ Filtres appliqués en tags
- ✅ Cartes de véhicules avec toutes les infos
- ✅ Badge de source sur chaque annonce
- ✅ Lien vers l'annonce originale

## 🚨 Notes importantes

1. **Marque obligatoire** : La recherche nécessite au moins une marque sélectionnée
2. **Scraping en temps réel** : Chaque recherche scrape les sites en direct (10-30s)
3. **Limites de pages** : Par défaut, 3 pages par source (configurable jusqu'à 10)
4. **Format unifié** : Les deux sources retournent le même format de données

## 🔮 Améliorations futures

- [ ] Sauvegarde des recherches
- [ ] Alertes email sur nouvelles annonces
- [ ] Export des résultats (CSV, PDF)
- [ ] Comparaison de véhicules
- [ ] Historique des prix
- [ ] Carte interactive des annonces
- [ ] Plus de filtres (couleur, nombre de portes, etc.)
- [ ] Plus de sources (ParuVendu, Argus, etc.)

## 📚 Documentation API complète

Voir `backend/SCRAPING_API.md` pour la documentation complète de l'API de scraping.
