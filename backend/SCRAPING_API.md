# API de Scraping - Documentation

## Vue d'ensemble

L'API de scraping permet d'extraire des annonces de véhicules depuis différentes sources en temps réel.

**Sources disponibles:**
- `leboncoin` - LeBonCoin.fr
- `lacentrale` - LaCentrale.fr
- `autoscout24` - AutoScout24.fr

## Endpoints

### 1. Scraper une source

```http
POST /api/scrape
Content-Type: application/json
```

**Corps de la requête:**

```json
{
  "source": "autoscout24",
  "max_pages": 3,
  "make": "volkswagen",
  "model": "golf",
  "max_price": 25000
}
```

**Paramètres:**

| Paramètre | Type | Requis | Description | Valeurs |
|-----------|------|--------|-------------|---------|
| `source` | string | ✅ | Source à scraper | `leboncoin`, `lacentrale`, `autoscout24` |
| `max_pages` | integer | ❌ | Nombre de pages (1-20) | Défaut: 3 |
| `query` | string | ❌ | Recherche (leboncoin) | Ex: "volkswagen golf" |
| `make` | string | ❌ | Marque | Ex: "volkswagen" |
| `model` | string | ❌ | Modèle | Ex: "golf" |
| `min_year` | integer | ❌ | Année minimale | Ex: 2015 |
| `max_year` | integer | ❌ | Année maximale | Ex: 2023 |
| `max_price` | integer | ❌ | Prix maximum | Ex: 25000 |
| `fuel_type` | string | ❌ | Type de carburant | `B` (essence), `D` (diesel), `E` (électrique) |
| `location` | string | ❌ | Localisation (leboncoin) | Ex: "Paris" |
| `deep_scrape` | boolean | ❌ | Scraping approfondi (leboncoin) | Défaut: false |

**Réponse:**

```json
{
  "success": true,
  "source": "autoscout24",
  "count": 45,
  "results": [
    {
      "source_ids": {
        "autoscout24": "abc123"
      },
      "title": "Volkswagen Golf GTI",
      "make": "Volkswagen",
      "model": "Golf GTI",
      "price": 22500,
      "year": 2019,
      "mileage": 45000,
      "fuel_type": "Essence",
      "transmission": "Manuelle",
      "location_city": "Paris",
      "url": "https://www.autoscout24.fr/annonces/...",
      "images": ["https://..."]
    }
  ],
  "duration": 12.5,
  "timestamp": "2025-11-21T19:30:00",
  "message": "45 véhicules trouvés"
}
```

### 2. Lister les sources disponibles

```http
GET /api/scrape/sources
```

**Réponse:**

```json
{
  "sources": {
    "leboncoin": {
      "name": "LeBonCoin",
      "url": "https://www.leboncoin.fr",
      "available": true,
      "filters": ["query", "max_price", "location", "deep_scrape"]
    },
    "lacentrale": {
      "name": "La Centrale",
      "url": "https://www.lacentrale.fr",
      "available": true,
      "filters": ["make", "model", "max_pages"]
    },
    "autoscout24": {
      "name": "AutoScout24",
      "url": "https://www.autoscout24.fr",
      "available": true,
      "filters": ["make", "model", "min_year", "max_year", "max_price", "fuel_type"]
    }
  },
  "total": 3
}
```

### 3. Vérifier le statut du système

```http
GET /api/scrape/status
```

**Réponse:**

```json
{
  "status": "operational",
  "scrapers": {
    "leboncoin": {
      "available": true,
      "status": "ready"
    },
    "lacentrale": {
      "available": true,
      "status": "ready"
    },
    "autoscout24": {
      "available": true,
      "status": "ready"
    }
  },
  "timestamp": "2025-11-21T19:30:00"
}
```

## Exemples d'utilisation

### Exemple 1: Scraper AutoScout24 sans filtres

```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "autoscout24",
    "max_pages": 1
  }'
```

### Exemple 2: Scraper AutoScout24 avec filtres

```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "autoscout24",
    "max_pages": 3,
    "make": "volkswagen",
    "model": "golf",
    "min_year": 2015,
    "max_year": 2023,
    "max_price": 25000,
    "fuel_type": "D"
  }'
```

### Exemple 3: Scraper LeBonCoin

```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "leboncoin",
    "query": "volkswagen golf",
    "max_pages": 5,
    "max_price": 20000,
    "deep_scrape": true
  }'
```

### Exemple 4: Scraper LaCentrale

```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "lacentrale",
    "make": "volkswagen",
    "model": "golf",
    "max_pages": 3
  }'
```

## Utilisation depuis le frontend

### JavaScript / Fetch API

```javascript
async function scrapeVehicles(params) {
  const response = await fetch('http://localhost:8000/api/scrape', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params)
  });

  const data = await response.json();

  if (data.success) {
    console.log(`✅ ${data.count} véhicules trouvés en ${data.duration}s`);
    return data.results;
  } else {
    console.error(`❌ Erreur: ${data.message}`);
    return [];
  }
}

// Utilisation
const results = await scrapeVehicles({
  source: 'autoscout24',
  max_pages: 3,
  make: 'volkswagen',
  model: 'golf',
  max_price: 25000
});
```

### React / Axios

```javascript
import axios from 'axios';

const scrapeVehicles = async (params) => {
  try {
    const { data } = await axios.post('http://localhost:8000/api/scrape', params);

    if (data.success) {
      console.log(`✅ ${data.count} véhicules trouvés`);
      return data.results;
    }
  } catch (error) {
    console.error('❌ Erreur scraping:', error);
    return [];
  }
};

// Utilisation dans un composant
const handleScrape = async () => {
  const results = await scrapeVehicles({
    source: 'autoscout24',
    max_pages: 1,
    make: 'volkswagen'
  });

  setVehicles(results);
};
```

## Notes importantes

1. **Performance**: Le scraping peut prendre plusieurs secondes selon le nombre de pages
2. **Rate limiting**: Évitez de faire trop de requêtes en peu de temps
3. **Gestion des erreurs**: Toujours vérifier `success: true` dans la réponse
4. **Filtres**: Chaque source supporte des filtres différents (voir tableau)
5. **Compatibilité**: Tous les scrapers retournent le même format de données

## Codes d'erreur

| Code | Description |
|------|-------------|
| 400 | Source invalide ou paramètres incorrects |
| 500 | Erreur interne du scraper |
| 503 | Service temporairement indisponible |

## Limitations

- **max_pages**: Maximum 20 pages par requête
- **Timeout**: 30 secondes par page
- **Débit**: Recommandé max 10 requêtes/minute
