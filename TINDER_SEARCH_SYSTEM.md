# 🔥 Système de Recherche Personnalisée avec Interface Tinder

## 📋 Vue d'ensemble

Ce système permet aux **particuliers** de créer des demandes de recherche personnalisée de véhicules. Les **experts/professionnels** peuvent alors prendre en charge ces demandes, proposer des véhicules, et recevoir du feedback en temps réel via une interface type Tinder.

---

## 🎯 Fonctionnalités Principales

### ✅ Pour les Particuliers

1. **Création de demandes** (réservé aux particuliers uniquement)
   - Description détaillée de leurs besoins
   - Critères : budget, carburant, kilométrage, année, etc.

2. **Évaluation des propositions en mode Tinder**
   - Interface swipe intuitive
   - 3 actions possibles :
     - ❌ **Refuser** : Véhicule ne correspond pas
     - 👍 **Liker** : Véhicule intéressant
     - ❤️ **Coup de foudre** : Véhicule parfait !
   - Feedback obligatoire sur les refus
   - Feedback optionnel sur les likes

3. **Suivi de leurs demandes**
   - Voir toutes les propositions reçues
   - Statistiques : propositions, coups de cœur, refus

### ✅ Pour les Experts/Professionnels

1. **Consultation des demandes disponibles**
   - Uniquement les demandes de particuliers
   - Assignation exclusive (un seul expert par demande)

2. **Proposition de véhicules**
   - Recherche dans leur stock ou la base de données
   - Ajout d'un message personnalisé

3. **Consultation des feedbacks**
   - Voir les réactions des clients
   - Taux d'acceptation, super likes
   - Affiner les recherches en fonction des retours

---

## 🚀 Guide d'Utilisation

### Pour les Particuliers

#### 1. Créer une demande

```bash
POST /api/assisted/requests
```

**Exemple de requête :**
```json
{
  "description": "Je cherche une citadine économique pour mes trajets quotidiens",
  "budget_max": 15000,
  "preferred_fuel_type": "essence",
  "preferred_transmission": "manuelle",
  "max_mileage": 80000,
  "min_year": 2018
}
```

**Restrictions :**
- ⚠️ Seuls les utilisateurs avec le rôle `PARTICULAR` peuvent créer des demandes
- Les professionnels recevront une erreur 403

#### 2. Accéder au mode Tinder

**URL Frontend :** `/assisted/requests/{requestId}/tinder`

**Route API :**
```bash
GET /api/assisted/requests/{requestId}/tinder/next
```

Cette route retourne la prochaine proposition non évaluée avec tous les détails du véhicule.

#### 3. Évaluer une proposition

**Option 1 : Liker**
```bash
POST /api/assisted/proposals/{proposalId}/tinder/like
Content-Type: application/json

{
  "feedback": "Bon rapport qualité-prix"
}
```

**Option 2 : Coup de foudre**
```bash
POST /api/assisted/proposals/{proposalId}/tinder/super-like
Content-Type: application/json

{
  "feedback": "Exactement ce que je cherchais !"
}
```

**Option 3 : Refuser**
```bash
POST /api/assisted/proposals/{proposalId}/tinder/reject
Content-Type: application/json

{
  "feedback": "Prix trop élevé pour mon budget"  // OBLIGATOIRE
}
```

---

### Pour les Experts

#### 1. Voir les demandes disponibles

```bash
GET /api/assisted/requests?status_filter=PENDING
```

**Filtre automatique :**
- Uniquement les demandes de **particuliers**
- Uniquement les demandes **non assignées**

#### 2. Prendre en charge une demande

```bash
POST /api/assisted/requests/{requestId}/accept
```

**Effet :**
- Vous devenez l'expert assigné
- La demande passe en statut `IN_PROGRESS`
- Aucun autre expert ne peut la prendre

#### 3. Proposer un véhicule

```bash
POST /api/assisted/requests/{requestId}/propose
Content-Type: application/json

{
  "vehicle_id": "abc-123",
  "message": "Ce véhicule correspond parfaitement à vos critères. Excellent état, faible kilométrage."
}
```

#### 4. Consulter les feedbacks

```bash
GET /api/assisted/requests/{requestId}/feedback
```

**Réponse :**
```json
{
  "request_id": "req-123",
  "total_evaluated": 10,
  "stats": {
    "liked": 4,
    "super_liked": 2,
    "rejected": 4,
    "positive_rate": 60.0
  },
  "feedbacks": [
    {
      "proposal_id": "prop-1",
      "vehicle_id": "v-123",
      "vehicle_title": "Peugeot 208 Active",
      "status": "SUPER_LIKED",
      "client_feedback": "Exactement ce que je cherchais !",
      "created_at": "2025-01-15T10:30:00Z"
    },
    {
      "proposal_id": "prop-2",
      "vehicle_id": "v-456",
      "vehicle_title": "Renault Clio",
      "status": "REJECTED",
      "client_feedback": "Prix trop élevé",
      "rejection_reason": "Prix trop élevé",
      "created_at": "2025-01-15T11:00:00Z"
    }
  ]
}
```

---

## 🗄️ Modifications de la Base de Données

### Migration

Pour appliquer les nouvelles modifications :

```bash
cd backend
alembic upgrade head
```

### Changements

1. **Nouveaux statuts dans `ProposalStatus`**
   - `LIKED` (remplace `FAVORITE`)
   - `SUPER_LIKED` (nouveau - coup de foudre)
   - `REJECTED` (inchangé)
   - `PENDING` (inchangé)

2. **Nouvelle colonne dans `proposed_vehicles`**
   - `client_feedback` (TEXT, nullable)
   - Stocke les commentaires du client sur chaque proposition

3. **Migration automatique**
   - Les anciennes propositions `FAVORITE` sont migrées vers `LIKED`

---

## 🎨 Interface Frontend (React)

### Composant : `TinderProposalsPage.jsx`

**Caractéristiques :**
- ✅ Affichage en mode carte
- ✅ Images du véhicule
- ✅ Détails complets (prix, année, kilométrage, etc.)
- ✅ Message personnalisé de l'expert
- ✅ 3 boutons d'action avec animations
- ✅ Modal de feedback avec suggestions rapides
- ✅ Animation de swipe gauche/droite
- ✅ Chargement automatique de la prochaine proposition

### Intégration dans votre application

Ajoutez cette route dans votre routeur React :

```jsx
import TinderProposalsPage from './Pages/TinderProposalsPage'

// Dans votre router
<Route
  path="/assisted/requests/:requestId/tinder"
  element={<TinderProposalsPage />}
/>
```

---

## 📊 Statistiques Expert

Les statistiques suivantes sont disponibles :

```bash
GET /api/assisted/expert/stats
```

**Réponse :**
```json
{
  "total_requests": 15,
  "pending_requests": 3,
  "completed_requests": 10,
  "total_proposals": 45,
  "accepted_proposals": 20,
  "super_liked_proposals": 8,
  "acceptance_rate": 44.4
}
```

---

## 🔐 Permissions et Restrictions

| Action | Particulier | Professionnel | Expert |
|--------|-------------|---------------|--------|
| Créer une demande | ✅ | ❌ | ❌ |
| Voir les demandes | ✅ (siennes) | ❌ | ✅ (disponibles + assignées) |
| Accepter une demande | ❌ | ❌ | ✅ |
| Proposer un véhicule | ❌ | ❌ | ✅ (si assigné) |
| Évaluer une proposition (Tinder) | ✅ (siennes) | ❌ | ❌ |
| Voir les feedbacks | ❌ | ❌ | ✅ (ses demandes) |

---

## 🔄 Workflow Complet

```
1. Particulier crée une demande
   └─> POST /api/assisted/requests

2. Expert voit la demande disponible
   └─> GET /api/assisted/requests?status_filter=PENDING

3. Expert accepte la demande (devient exclusif)
   └─> POST /api/assisted/requests/{id}/accept

4. Expert propose des véhicules
   └─> POST /api/assisted/requests/{id}/propose

5. Particulier accède au mode Tinder
   └─> Frontend: /assisted/requests/{id}/tinder

6. Particulier évalue chaque proposition
   ├─> POST /api/assisted/proposals/{id}/tinder/like
   ├─> POST /api/assisted/proposals/{id}/tinder/super-like
   └─> POST /api/assisted/proposals/{id}/tinder/reject

7. Expert consulte les feedbacks
   └─> GET /api/assisted/requests/{id}/feedback

8. Expert affine et propose de nouveaux véhicules
   └─> Retour à l'étape 4

9. Expert marque la demande comme terminée
   └─> POST /api/assisted/requests/{id}/complete
```

---

## 🎯 Avantages du Système

### Pour les Clients
- ✅ Interface ludique et intuitive (type Tinder)
- ✅ Évaluation rapide des propositions
- ✅ Feedback facile avec suggestions pré-remplies
- ✅ Expert dédié qui affine ses propositions

### Pour les Experts
- ✅ Demandes exclusives (pas de compétition)
- ✅ Feedback en temps réel pour s'améliorer
- ✅ Statistiques détaillées (taux d'acceptation, coups de cœur)
- ✅ Apprentissage des préférences clients

---

## 🛠️ Configuration Technique

### Variables d'environnement (Frontend)

```env
VITE_API_URL=http://localhost:8000
```

### Dépendances

**Backend :**
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

**Frontend :**
- React 18+
- React Router DOM

---

## 📝 Exemples de Code

### Créer une demande (JavaScript/Fetch)

```javascript
const createRequest = async (token) => {
  const response = await fetch('http://localhost:8000/api/assisted/requests', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      description: 'Je cherche une voiture familiale spacieuse',
      budget_max: 25000,
      preferred_fuel_type: 'diesel',
      max_mileage: 100000,
      min_year: 2019
    })
  })

  const data = await response.json()
  console.log('Demande créée:', data.id)
}
```

### Évaluer une proposition en Tinder mode

```javascript
const superLikeProposal = async (proposalId, token) => {
  const response = await fetch(
    `http://localhost:8000/api/assisted/proposals/${proposalId}/tinder/super-like`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        feedback: 'Parfait ! Couleur magnifique et très bon prix'
      })
    }
  )

  const data = await response.json()
  console.log('Proposition super-likée:', data)
}
```

---

## 🐛 Débogage

### Problème : "Seuls les particuliers peuvent créer des demandes"

**Solution :** Vérifiez que le rôle de l'utilisateur est bien `PARTICULAR` :

```sql
SELECT id, email, role FROM users WHERE email = 'votre@email.com';
```

Pour changer le rôle :

```sql
UPDATE users SET role = 'PARTICULAR' WHERE email = 'votre@email.com';
```

### Problème : "Demande déjà prise en charge"

**Solution :** Un autre expert a déjà accepté cette demande. Cherchez une autre demande disponible.

---

## 📞 Support

Pour toute question ou problème, consultez :
- La documentation API : `/docs` (Swagger)
- Les logs backend : `backend/logs/`
- Le code source : `backend/app/routes/assisted.py`

---

## 🎉 C'est parti !

Votre système de recherche personnalisée type Tinder est maintenant prêt à être utilisé ! 🚀

N'oubliez pas de :
1. ✅ Appliquer la migration Alembic
2. ✅ Redémarrer le serveur backend
3. ✅ Tester le nouveau composant frontend
4. ✅ Créer quelques utilisateurs de test (particuliers et experts)
