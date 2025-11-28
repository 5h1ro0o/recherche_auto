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
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
      paddingBottom: '60px',
    }}>
      {/* Header Section */}
      <div style={{
        background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)',
        color: 'white',
        padding: '60px 20px',
        textAlign: 'center',
        marginBottom: '40px',
      }}>
        <h1 style={{
          fontSize: '42px',
          fontWeight: 700,
          margin: '0 0 16px 0',
          lineHeight: 1.2,
        }}>
          📚 Encyclopédie Automobile
        </h1>
        <p style={{
          fontSize: '18px',
          margin: 0,
          opacity: 0.95,
        }}>
          Toutes les connaissances nécessaires pour choisir et acheter votre véhicule en toute confiance
        </p>
      </div>

      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 20px',
      }}>
        {/* Search Bar */}
        <div style={{
          marginBottom: '32px',
        }}>
          <input
            type="text"
            placeholder="🔍 Rechercher dans l'encyclopédie..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              maxWidth: '600px',
              padding: '14px 20px',
              fontSize: '16px',
              border: '2px solid #E5E7EB',
              borderRadius: '12px',
              outline: 'none',
              transition: 'all 0.2s',
              fontFamily: 'inherit',
              display: 'block',
              margin: '0 auto',
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#4F46E5'
              e.target.style.boxShadow = '0 0 0 3px rgba(79, 70, 229, 0.1)'
            }}
            onBlur={(e) => {
              e.target.style.borderColor = '#E5E7EB'
              e.target.style.boxShadow = 'none'
            }}
          />
        </div>

        {/* Category Tabs */}
        <div style={{
          display: 'flex',
          gap: '12px',
          marginBottom: '32px',
          flexWrap: 'wrap',
          justifyContent: 'center',
        }}>
          {[
            { id: 'brands', label: '🏭 Marques' },
            { id: 'fuelTypes', label: '⛽ Types de carburant' },
            { id: 'buyingGuide', label: '📖 Guide d\'achat' },
            { id: 'glossary', label: '📝 Glossaire' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedCategory(tab.id)}
              style={{
                padding: '12px 24px',
                background: selectedCategory === tab.id ? '#4F46E5' : 'white',
                color: selectedCategory === tab.id ? 'white' : '#222222',
                border: selectedCategory === tab.id ? 'none' : '2px solid #E5E7EB',
                borderRadius: '12px',
                fontSize: '15px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                if (selectedCategory !== tab.id) {
                  e.target.style.borderColor = '#4F46E5'
                }
              }}
              onMouseLeave={(e) => {
                if (selectedCategory !== tab.id) {
                  e.target.style.borderColor = '#E5E7EB'
                }
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div>
          {/* Brands */}
          {selectedCategory === 'brands' && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
              gap: '24px',
            }}>
              {filteredData().map(brand => (
                <div
                  key={brand.id}
                  style={{
                    background: 'white',
                    borderRadius: '12px',
                    padding: '24px',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                    border: '1px solid #EEEEEE',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)'
                    e.currentTarget.style.boxShadow = '0 12px 40px rgba(0,0,0,0.12)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)'
                    e.currentTarget.style.boxShadow = '0 1px 2px rgba(0,0,0,0.04)'
                  }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '16px',
                  }}>
                    <span style={{ fontSize: '32px' }}>{brand.logo}</span>
                    <h3 style={{
                      margin: 0,
                      fontSize: '22px',
                      fontWeight: 700,
                      color: '#222222',
                    }}>
                      {brand.name}
                    </h3>
                  </div>
                  <p style={{
                    fontSize: '14px',
                    lineHeight: 1.6,
                    color: '#6B7280',
                    marginBottom: '16px',
                  }}>
                    {brand.description}
                  </p>
                  <div style={{ marginBottom: '16px' }}>
                    <strong style={{
                      fontSize: '13px',
                      color: '#222222',
                      display: 'block',
                      marginBottom: '8px',
                    }}>
                      Modèles populaires :
                    </strong>
                    <div style={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: '8px',
                    }}>
                      {brand.popularModels.map((model, idx) => (
                        <span
                          key={idx}
                          style={{
                            background: '#EEF2FF',
                            color: '#4F46E5',
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '13px',
                            fontWeight: 500,
                          }}
                        >
                          {model}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div style={{
                    padding: '12px',
                    background: '#F9FAFB',
                    borderRadius: '8px',
                    fontSize: '13px',
                    color: '#6B7280',
                  }}>
                    <strong style={{ color: '#222222' }}>Réputation :</strong> {brand.reputation}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Fuel Types */}
          {selectedCategory === 'fuelTypes' && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
              gap: '24px',
            }}>
              {filteredData().map(fuel => (
                <div
                  key={fuel.id}
                  style={{
                    background: 'white',
                    borderRadius: '12px',
                    padding: '24px',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                    border: '1px solid #EEEEEE',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)'
                    e.currentTarget.style.boxShadow = '0 12px 40px rgba(0,0,0,0.12)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)'
                    e.currentTarget.style.boxShadow = '0 1px 2px rgba(0,0,0,0.04)'
                  }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '20px',
                  }}>
                    <span style={{ fontSize: '32px' }}>{fuel.icon}</span>
                    <h3 style={{
                      margin: 0,
                      fontSize: '22px',
                      fontWeight: 700,
                      color: '#222222',
                    }}>
                      {fuel.name}
                    </h3>
                  </div>
                  <div style={{ marginBottom: '16px' }}>
                    <h4 style={{
                      margin: '0 0 12px 0',
                      fontSize: '15px',
                      fontWeight: 600,
                      color: '#10B981',
                    }}>
                      ✅ Avantages
                    </h4>
                    <ul style={{
                      margin: 0,
                      paddingLeft: '20px',
                      fontSize: '14px',
                      color: '#6B7280',
                      lineHeight: 1.8,
                    }}>
                      {fuel.pros.map((pro, idx) => (
                        <li key={idx}>{pro}</li>
                      ))}
                    </ul>
                  </div>
                  <div style={{ marginBottom: '16px' }}>
                    <h4 style={{
                      margin: '0 0 12px 0',
                      fontSize: '15px',
                      fontWeight: 600,
                      color: '#EF4444',
                    }}>
                      ❌ Inconvénients
                    </h4>
                    <ul style={{
                      margin: 0,
                      paddingLeft: '20px',
                      fontSize: '14px',
                      color: '#6B7280',
                      lineHeight: 1.8,
                    }}>
                      {fuel.cons.map((con, idx) => (
                        <li key={idx}>{con}</li>
                      ))}
                    </ul>
                  </div>
                  <div style={{
                    padding: '12px',
                    background: '#EEF2FF',
                    borderRadius: '8px',
                    fontSize: '13px',
                    color: '#4F46E5',
                    borderLeft: '4px solid #4F46E5',
                  }}>
                    <strong>Idéal pour :</strong> {fuel.idealFor}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Buying Guide */}
          {selectedCategory === 'buyingGuide' && (
            <div style={{
              maxWidth: '900px',
              margin: '0 auto',
            }}>
              {filteredData().map((step, idx) => (
                <div
                  key={step.id}
                  style={{
                    background: 'white',
                    borderRadius: '12px',
                    padding: '24px',
                    marginBottom: '16px',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                    border: '1px solid #EEEEEE',
                    display: 'flex',
                    gap: '20px',
                    alignItems: 'flex-start',
                  }}
                >
                  <div style={{
                    fontSize: '40px',
                    flexShrink: 0,
                  }}>
                    {step.icon}
                  </div>
                  <div style={{ flex: 1 }}>
                    <h3 style={{
                      margin: '0 0 12px 0',
                      fontSize: '20px',
                      fontWeight: 700,
                      color: '#222222',
                    }}>
                      {step.id}. {step.title}
                    </h3>
                    <p style={{
                      margin: 0,
                      fontSize: '15px',
                      lineHeight: 1.7,
                      color: '#6B7280',
                    }}>
                      {step.content}
                    </p>
                  </div>
                </div>
              ))}
              <div style={{
                background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)',
                borderRadius: '16px',
                padding: '40px',
                textAlign: 'center',
                color: 'white',
                marginTop: '32px',
              }}>
                <h3 style={{
                  fontSize: '28px',
                  fontWeight: 700,
                  margin: '0 0 12px 0',
                }}>
                  Prêt à chercher votre véhicule ?
                </h3>
                <p style={{
                  fontSize: '16px',
                  margin: '0 0 24px 0',
                  opacity: 0.95,
                }}>
                  Utilisez notre recherche avancée pour trouver le véhicule qui correspond à tous ces critères
                </p>
                <Link
                  to="/search"
                  style={{
                    display: 'inline-block',
                    padding: '14px 32px',
                    background: 'white',
                    color: '#4F46E5',
                    textDecoration: 'none',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: 600,
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)'
                    e.target.style.boxShadow = '0 8px 24px rgba(0,0,0,0.2)'
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)'
                    e.target.style.boxShadow = 'none'
                  }}
                >
                  🔍 Lancer une recherche
                </Link>
              </div>
            </div>
          )}

          {/* Glossary */}
          {selectedCategory === 'glossary' && (
            <div style={{
              maxWidth: '900px',
              margin: '0 auto',
            }}>
              {filteredData().map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'white',
                    borderRadius: '12px',
                    padding: '20px 24px',
                    marginBottom: '12px',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                    border: '1px solid #EEEEEE',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#4F46E5'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#EEEEEE'
                  }}
                >
                  <dt style={{
                    fontSize: '17px',
                    fontWeight: 700,
                    color: '#4F46E5',
                    marginBottom: '8px',
                  }}>
                    {item.term}
                  </dt>
                  <dd style={{
                    margin: 0,
                    fontSize: '15px',
                    lineHeight: 1.7,
                    color: '#6B7280',
                  }}>
                    {item.definition}
                  </dd>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
