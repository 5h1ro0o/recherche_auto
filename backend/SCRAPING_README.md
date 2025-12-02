# 🌐 Web Scraping Automatique - Encyclopédie Automobile

Ce dossier contient tous les scripts de web scraping pour collecter automatiquement TOUTES les données automobiles depuis Internet.

## 📋 Scripts Disponibles

### 1. **scrape_models_web.py** - Scraping des modèles de voitures
Collecte automatiquement depuis :
- ✅ **API CarQuery** - Spécifications techniques
- ✅ **Automobile-Catalog** - Dimensions, performances, consommation
- ✅ **Caradisiac** - Avis utilisateurs, avantages/inconvénients
- ✅ **L'Argus** - Fiches techniques détaillées

**Données collectées** :
- Toutes les caractéristiques techniques (dimensions, poids, performances)
- Consommation réelle et émissions CO2
- Avantages et inconvénients
- Avis clients réels
- Notes de fiabilité

### 2. **scrape_engines_web.py** - Scraping des moteurs
Collecte automatiquement depuis :
- ✅ **Sites techniques spécialisés** - Spécifications moteurs
- ✅ **Caradisiac Fiabilité** - Notes de fiabilité et problèmes
- ✅ **Forums automobiles** - Retours d'expérience réels
- ✅ **L'Argus** - Données techniques et applications

**Données collectées** :
- Spécifications complètes (cylindrée, puissance, couple, compression)
- Notes de fiabilité réelles
- Avantages et inconvénients
- Problèmes communs recensés
- Avis d'experts et utilisateurs
- Coûts d'entretien

### 3. **scrape_transmissions_web.py** - Scraping des transmissions
Collecte automatiquement depuis :
- ✅ **Caradisiac** - Fiabilité des boîtes de vitesses
- ✅ **Forums spécialisés** - Retours utilisateurs
- ✅ **L'Argus** - Spécifications techniques
- ✅ **Sites techniques** - Détails constructeurs

**Données collectées** :
- Type et nombre de rapports
- Notes de fiabilité
- Avantages et inconvénients
- Problèmes communs (embrayages, mécatronique, etc.)
- Coûts de maintenance
- Avis utilisateurs réels

### 4. **run_all_scrapers.py** - Script principal
Lance tous les scrapers automatiquement en séquence avec statistiques détaillées.

## 🚀 Utilisation

### Méthode 1 : Lancer tous les scrapers (RECOMMANDÉ)

```bash
# Depuis le dossier backend/
python run_all_scrapers.py
```

Ce script va :
1. 🚗 Collecter tous les modèles pour toutes les marques
2. 🔧 Collecter tous les moteurs (essence, diesel, hybride)
3. ⚙️  Collecter toutes les transmissions (manuelles, auto, robotisées)
4. 📊 Afficher les statistiques complètes

### Méthode 2 : Lancer les scrapers individuellement

```bash
# Uniquement les modèles
python scrape_models_web.py

# Uniquement les moteurs
python scrape_engines_web.py

# Uniquement les transmissions
python scrape_transmissions_web.py
```

## 📦 Dépendances

Toutes les dépendances sont déjà dans `requirements.txt` :

```bash
pip install -r requirements.txt
```

Packages utilisés :
- `aiohttp` - Requêtes HTTP asynchrones
- `beautifulsoup4` - Parsing HTML
- `lxml` - Parser rapide pour BeautifulSoup
- `asyncio` - Programmation asynchrone

## ⚙️ Configuration

Les scrapers utilisent les variables d'environnement du fichier `.env` :

```env
DATABASE_URL=postgresql://user:password@localhost:5432/recherche_auto
```

## 📊 Sources de Données

### Sites de spécifications techniques
- **automobile-catalog.com** - Catalogue complet de véhicules
- **cars-data.com** - Base de données techniques
- **ultimatespecs.com** - Spécifications détaillées

### Sites d'avis et fiabilité
- **caradisiac.com** - Premier site auto français, forums très actifs
- **largus.fr** - L'Argus, référence historique
- **autoplus.fr** - Tests et essais détaillés
- **auto-moto.com** - Avis d'experts

### APIs automobiles
- **CarQuery API** - API gratuite de données automobiles
- **Auto-Data API** - Spécifications techniques

### Forums spécialisés
- **forum-auto.caradisiac.com** - Plus grand forum auto français
- **forum-peugeot.com** - Expertise Peugeot
- **forum-renault.com** - Expertise Renault
- **vwforum.com** - Expertise Volkswagen/Audi

## 🎯 Fonctionnalités

### Scraping Intelligent
- ✅ **Retry automatique** avec backoff exponentiel
- ✅ **Respect des serveurs** (délais entre requêtes)
- ✅ **Gestion des erreurs** robuste
- ✅ **Logging détaillé** de la progression
- ✅ **Sauvegarde par batch** pour éviter les pertes

### Extraction de Données
- ✅ **Parsing HTML** avec BeautifulSoup
- ✅ **Extraction intelligente** de nombres, textes, dates
- ✅ **Nettoyage automatique** des données
- ✅ **Fusion multi-sources** pour enrichissement

### Performance
- ✅ **Asynchrone** (aiohttp, asyncio)
- ✅ **Parallélisation** des requêtes
- ✅ **Session persistante** HTTP
- ✅ **Timeouts configurables**

## 📈 Résultats Attendus

Avec tous les scrapers, vous collecterez :

| Catégorie | Quantité estimée |
|-----------|-----------------|
| **Modèles** | 500-1000+ modèles |
| **Moteurs** | 100-200 moteurs |
| **Transmissions** | 30-50 boîtes |
| **TOTAL** | **630-1250 entrées** |

## ⚠️ Avertissements

### Légalité
- ✅ Les scrapers respectent les `robots.txt`
- ✅ Délais entre requêtes pour ne pas surcharger les serveurs
- ✅ Usage strictement personnel/éducatif
- ⚠️  Vérifiez les CGU des sites scrapés

### Limitations
- ⏱️  Le scraping complet peut prendre **2-4 heures**
- 🌐 Requiert une connexion Internet stable
- 📡 Certains sites peuvent bloquer après trop de requêtes
- 🔄 Certaines données peuvent ne pas être disponibles

### Maintenance
- 🔧 Les sites changent régulièrement leur structure HTML
- 🔄 Les sélecteurs CSS/classes peuvent devenir obsolètes
- ⚙️  Maintenance régulière des scrapers recommandée

## 🐛 Debugging

### Activer les logs détaillés

Modifier `echo=True` dans les scripts pour voir les requêtes SQL :

```python
engine = create_async_engine(DATABASE_URL, echo=True)
```

### Tester sur une seule marque

Modifier dans `run_all_scrapers.py` :

```python
for brand_id, brand_name in brands[:1]:  # Tester sur 1 marque seulement
```

### Voir les requêtes HTTP

Les scrapers affichent déjà :
- ✅ URLs visitées
- ✅ Status codes
- ✅ Erreurs de connexion

## 📝 Exemple de sortie

```
================================================================================
                 SCRAPING AUTOMATIQUE ENCYCLOPÉDIE AUTOMOBILE
                     Collecte TOUTES les données depuis Internet
================================================================================

┌──────────────────────────────────────────────────────────────────────────────┐
│                   🚗 SCRAPING DES MODÈLES AUTOMOBILES                        │
└──────────────────────────────────────────────────────────────────────────────┘

📋 57 marques trouvées
🌐 Sources : CarQuery API, Automobile-Catalog, Caradisiac, L'Argus

────────────────────────────────────────────────────────────────────────────────
Marque: Renault
────────────────────────────────────────────────────────────────────────────────

🔍 Scraping automobile-catalog.com pour Renault...
✅ Automobile Catalog: 45 modèles trouvés

💬 Scraping avis Caradisiac pour Renault Clio V...
✅ Renault: 45 modèles collectés

...

================================================================================
                             STATISTIQUES FINALES
================================================================================

📊 Modèles collectés      :    856
📊 Moteurs collectés      :    142
📊 Transmissions collectées:     38
──────────────────────────────────────────────
📊 TOTAL                  :   1036

⚠️  Erreurs               :      0

⏱️  Durée totale          : 02h 34m 18s

================================================================================

✅ Scraping terminé avec succès !
```

## 🤝 Contribution

Pour ajouter de nouvelles sources de données :

1. Identifier le site cible
2. Analyser la structure HTML
3. Créer les fonctions de scraping
4. Ajouter la gestion d'erreurs
5. Tester sur quelques exemples
6. Intégrer dans le scraper principal

## 📞 Support

En cas de problème :
1. Vérifier la connexion Internet
2. Vérifier que PostgreSQL est démarré
3. Vérifier les logs d'erreur
4. Tester sur une seule marque d'abord
5. Vérifier que les sites sources sont accessibles

---

**Note** : Ce système de scraping collecte des données publiques pour un usage personnel/éducatif. Respectez toujours les conditions d'utilisation des sites web.
