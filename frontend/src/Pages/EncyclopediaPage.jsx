// frontend/src/Pages/EncyclopediaPage.jsx
import React, { useState } from 'react'
import { Link } from 'react-router-dom'

export default function EncyclopediaPage() {
  const [selectedCategory, setSelectedCategory] = useState('brands')
  const [searchQuery, setSearchQuery] = useState('')

  // Données encyclopédiques (à enrichir selon vos besoins)
  const encyclopediaData = {
    brands: [
      {
        id: 1,
        name: 'Renault',
        logo: '🚗',
        description: 'Constructeur automobile français fondé en 1899, spécialisé dans les véhicules compacts et électriques.',
        popularModels: ['Clio', 'Megane', 'Captur', 'Zoe'],
        reputation: 'Fiabilité moyenne, bon rapport qualité-prix'
      },
      {
        id: 2,
        name: 'Peugeot',
        logo: '🦁',
        description: 'Marque automobile française historique, reconnue pour son design et son confort.',
        popularModels: ['208', '308', '3008', '5008'],
        reputation: 'Bon confort, finitions soignées'
      },
      {
        id: 3,
        name: 'Citroën',
        logo: '🔷',
        description: 'Constructeur français innovant, pionnier du confort avec la suspension hydraulique.',
        popularModels: ['C3', 'C4', 'C5 Aircross', 'Berlingo'],
        reputation: 'Confort exceptionnel, designs audacieux'
      },
      {
        id: 4,
        name: 'Volkswagen',
        logo: '⚙️',
        description: 'Constructeur allemand leader mondial, synonyme de qualité et fiabilité.',
        popularModels: ['Golf', 'Polo', 'Tiguan', 'ID.3'],
        reputation: 'Excellente fiabilité, finitions premium'
      },
      {
        id: 5,
        name: 'BMW',
        logo: '🔵',
        description: 'Marque allemande de prestige, spécialiste des berlines sportives.',
        popularModels: ['Série 1', 'Série 3', 'X1', 'X3'],
        reputation: 'Performances élevées, plaisir de conduite'
      },
      {
        id: 6,
        name: 'Mercedes-Benz',
        logo: '⭐',
        description: 'Constructeur allemand premium, référence en matière de luxe et technologie.',
        popularModels: ['Classe A', 'Classe C', 'GLA', 'GLC'],
        reputation: 'Luxe, confort et technologies de pointe'
      },
      {
        id: 7,
        name: 'Toyota',
        logo: '🔴',
        description: 'Constructeur japonais leader mondial, réputé pour sa fiabilité légendaire.',
        popularModels: ['Yaris', 'Corolla', 'RAV4', 'Prius'],
        reputation: 'Fiabilité exceptionnelle, hybride performant'
      },
      {
        id: 8,
        name: 'Tesla',
        logo: '⚡',
        description: 'Pionnier américain du véhicule électrique et de la conduite autonome.',
        popularModels: ['Model 3', 'Model Y', 'Model S', 'Model X'],
        reputation: 'Technologies avancées, performances électriques'
      }
    ],
    fuelTypes: [
      {
        id: 1,
        name: 'Essence',
        icon: '⛽',
        pros: ['Prix d\'achat inférieur', 'Entretien moins coûteux', 'Meilleur pour petits trajets'],
        cons: ['Consommation élevée sur autoroute', 'Émissions CO2 importantes', 'Prix du carburant élevé'],
        idealFor: 'Conducteurs urbains avec petits trajets quotidiens'
      },
      {
        id: 2,
        name: 'Diesel',
        icon: '🛢️',
        pros: ['Économique sur longs trajets', 'Couple élevé', 'Bonne autonomie'],
        cons: ['Prix d\'achat plus élevé', 'Entretien coûteux', 'Restrictions urbaines'],
        idealFor: 'Gros rouleurs (>20 000 km/an) sur autoroute'
      },
      {
        id: 3,
        name: 'Hybride',
        icon: '🔋',
        pros: ['Consommation réduite en ville', 'Bonus écologique', 'Confort de conduite'],
        cons: ['Prix d\'achat élevé', 'Batterie à remplacer', 'Poids important'],
        idealFor: 'Trajets mixtes ville/route, conscience écologique'
      },
      {
        id: 4,
        name: 'Électrique',
        icon: '⚡',
        pros: ['Zéro émission', 'Coût d\'usage très faible', 'Silence et confort', 'Aides à l\'achat'],
        cons: ['Autonomie limitée', 'Temps de recharge', 'Prix d\'achat élevé', 'Infrastructure de recharge'],
        idealFor: 'Trajets quotidiens prévisibles avec possibilité de recharge'
      },
      {
        id: 5,
        name: 'GPL',
        icon: '💨',
        pros: ['Carburant très économique', 'Émissions réduites', 'Double alimentation essence/GPL'],
        cons: ['Réseau de stations limité', 'Coffre réduit (réservoir GPL)', 'Installation coûteuse'],
        idealFor: 'Gros rouleurs cherchant économies maximales'
      }
    ],
    buyingGuide: [
      {
        id: 1,
        title: 'Définir son budget',
        icon: '💰',
        content: 'Incluez le prix d\'achat, l\'assurance, l\'entretien et le carburant. Règle générale : le coût mensuel total ne devrait pas dépasser 20% de vos revenus.'
      },
      {
        id: 2,
        title: 'Analyser ses besoins',
        icon: '📊',
        content: 'Kilométrage annuel, type de trajets (ville/autoroute), nombre de places nécessaires, besoin de coffre. Ces critères détermineront le type de véhicule et de motorisation.'
      },
      {
        id: 3,
        title: 'Vérifier l\'historique',
        icon: '📋',
        content: 'Pour l\'occasion : carnet d\'entretien, rapport Histovec, contrôle technique, nombre de propriétaires. Méfiez-vous des véhicules sans historique.'
      },
      {
        id: 4,
        title: 'Essai routier',
        icon: '🚗',
        content: 'Testez le véhicule dans des conditions variées : ville, route, autoroute. Vérifiez bruits anormaux, tenue de route, confort, visibilité et équipements.'
      },
      {
        id: 5,
        title: 'Inspection mécanique',
        icon: '🔧',
        content: 'Pour l\'occasion, faites inspecter le véhicule par un professionnel avant achat. Coût : 100-200€, économies potentielles : plusieurs milliers d\'euros.'
      },
      {
        id: 6,
        title: 'Négocier le prix',
        icon: '💬',
        content: 'Comparez avec les prix du marché (Argus, annonces similaires). Les défauts identifiés sont des arguments de négociation. Négociation moyenne : 5-10% du prix affiché.'
      }
    ],
    glossary: [
      { term: 'Chevaux fiscaux (CV)', definition: 'Unité administrative française pour calculer le coût de la carte grise, basée sur puissance et émissions CO2.' },
      { term: 'Couple moteur (Nm)', definition: 'Force de rotation du moteur. Plus il est élevé, meilleures sont les reprises et accélérations.' },
      { term: 'Puissance (Ch/kW)', definition: 'Capacité maximale du moteur. Influence la vitesse de pointe et les performances générales.' },
      { term: 'Cote Argus', definition: 'Valeur de référence d\'un véhicule d\'occasion basée sur l\'offre et la demande du marché.' },
      { term: 'Malus écologique', definition: 'Taxe appliquée aux véhicules neufs émettant plus de 117g CO2/km (barème 2024).' },
      { term: 'Garantie constructeur', definition: 'Garantie légale minimale de 2 ans, certains constructeurs offrent jusqu\'à 7 ans.' },
      { term: 'Contrôle technique', definition: 'Obligatoire tous les 2 ans pour véhicules de plus de 4 ans. Vérifie sécurité et pollution.' },
      { term: 'FAP', definition: 'Filtre à Particules. Équipement obligatoire sur diesels, capte les particules fines. Coût remplacement : 500-2000€.' },
      { term: 'Turbo', definition: 'Système augmentant la puissance du moteur en comprimant l\'air. Améliore performances sans augmenter cylindrée.' },
      { term: 'Boîte DSG/EDC', definition: 'Boîte automatique à double embrayage. Confort de l\'auto avec efficacité de la manuelle.' }
    ]
  }

  const filteredData = () => {
    const data = encyclopediaData[selectedCategory]
    if (!searchQuery) return data

    return data.filter(item =>
      JSON.stringify(item).toLowerCase().includes(searchQuery.toLowerCase())
    )
  }

  return (
    <div className="encyclopedia-page">
      <div className="encyclopedia-header">
        <h1>📚 Encyclopédie Automobile</h1>
        <p>
          Toutes les connaissances nécessaires pour choisir et acheter votre véhicule
          en toute confiance
        </p>
      </div>

      {/* Search Bar */}
      <div className="encyclopedia-search">
        <input
          type="text"
          placeholder="Rechercher dans l'encyclopédie..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      {/* Category Tabs */}
      <div className="category-tabs">
        <button
          className={`tab ${selectedCategory === 'brands' ? 'active' : ''}`}
          onClick={() => setSelectedCategory('brands')}
        >
          🏭 Marques
        </button>
        <button
          className={`tab ${selectedCategory === 'fuelTypes' ? 'active' : ''}`}
          onClick={() => setSelectedCategory('fuelTypes')}
        >
          ⛽ Types de carburant
        </button>
        <button
          className={`tab ${selectedCategory === 'buyingGuide' ? 'active' : ''}`}
          onClick={() => setSelectedCategory('buyingGuide')}
        >
          📖 Guide d'achat
        </button>
        <button
          className={`tab ${selectedCategory === 'glossary' ? 'active' : ''}`}
          onClick={() => setSelectedCategory('glossary')}
        >
          📝 Glossaire
        </button>
      </div>

      {/* Content */}
      <div className="encyclopedia-content">
        {/* Brands */}
        {selectedCategory === 'brands' && (
          <div className="brands-grid">
            {filteredData().map(brand => (
              <div key={brand.id} className="brand-card">
                <div className="brand-header">
                  <span className="brand-logo">{brand.logo}</span>
                  <h3>{brand.name}</h3>
                </div>
                <p className="brand-description">{brand.description}</p>
                <div className="brand-section">
                  <strong>Modèles populaires :</strong>
                  <div className="model-tags">
                    {brand.popularModels.map((model, idx) => (
                      <span key={idx} className="model-tag">{model}</span>
                    ))}
                  </div>
                </div>
                <div className="brand-reputation">
                  <strong>Réputation :</strong> {brand.reputation}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Fuel Types */}
        {selectedCategory === 'fuelTypes' && (
          <div className="fuel-types-grid">
            {filteredData().map(fuel => (
              <div key={fuel.id} className="fuel-card">
                <div className="fuel-header">
                  <span className="fuel-icon">{fuel.icon}</span>
                  <h3>{fuel.name}</h3>
                </div>
                <div className="fuel-section">
                  <h4 className="pros-title">✅ Avantages</h4>
                  <ul>
                    {fuel.pros.map((pro, idx) => (
                      <li key={idx}>{pro}</li>
                    ))}
                  </ul>
                </div>
                <div className="fuel-section">
                  <h4 className="cons-title">❌ Inconvénients</h4>
                  <ul>
                    {fuel.cons.map((con, idx) => (
                      <li key={idx}>{con}</li>
                    ))}
                  </ul>
                </div>
                <div className="fuel-ideal">
                  <strong>Idéal pour :</strong> {fuel.idealFor}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Buying Guide */}
        {selectedCategory === 'buyingGuide' && (
          <div className="buying-guide">
            {filteredData().map(step => (
              <div key={step.id} className="guide-step">
                <div className="step-icon">{step.icon}</div>
                <div className="step-content">
                  <h3>{step.id}. {step.title}</h3>
                  <p>{step.content}</p>
                </div>
              </div>
            ))}
            <div className="guide-cta">
              <h3>Prêt à chercher votre véhicule ?</h3>
              <p>Utilisez notre recherche avancée pour trouver le véhicule qui correspond à tous ces critères</p>
              <Link to="/search" className="btn-primary">
                Lancer une recherche
              </Link>
            </div>
          </div>
        )}

        {/* Glossary */}
        {selectedCategory === 'glossary' && (
          <div className="glossary-list">
            {filteredData().map((item, idx) => (
              <div key={idx} className="glossary-item">
                <dt className="glossary-term">{item.term}</dt>
                <dd className="glossary-definition">{item.definition}</dd>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
