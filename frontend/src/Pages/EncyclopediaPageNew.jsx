// frontend/src/Pages/EncyclopediaPageNew.jsx
import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function EncyclopediaPageNew() {
  const [selectedCategory, setSelectedCategory] = useState('brands')
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)

  // États pour les données
  const [brands, setBrands] = useState([])
  const [models, setModels] = useState([])
  const [engines, setEngines] = useState([])
  const [transmissions, setTransmissions] = useState([])
  const [fuelTypesStats, setFuelTypesStats] = useState([])
  const [selectedItem, setSelectedItem] = useState(null)

  // Charger les données en fonction de la catégorie
  useEffect(() => {
    loadData()
  }, [selectedCategory, searchQuery])

  const loadData = async () => {
    setLoading(true)
    try {
      switch (selectedCategory) {
        case 'brands':
          const brandsRes = await axios.get(`${API_URL}/encyclopedia/brands`, {
            params: { search: searchQuery || undefined, limit: 100 }
          })
          setBrands(brandsRes.data)
          break

        case 'models':
          const modelsRes = await axios.get(`${API_URL}/encyclopedia/models`, {
            params: { search: searchQuery || undefined, limit: 100 }
          })
          setModels(modelsRes.data)
          break

        case 'engines':
          const enginesRes = await axios.get(`${API_URL}/encyclopedia/engines`, {
            params: { search: searchQuery || undefined, limit: 100 }
          })
          setEngines(enginesRes.data)
          break

        case 'transmissions':
          const transRes = await axios.get(`${API_URL}/encyclopedia/transmissions`, {
            params: { search: searchQuery || undefined, limit: 100 }
          })
          setTransmissions(transRes.data)
          break

        case 'fuelTypes':
          const fuelRes = await axios.get(`${API_URL}/encyclopedia/stats/fuel-types`)
          setFuelTypesStats(fuelRes.data)
          break
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error)
    } finally {
      setLoading(false)
    }
  }

  const viewDetails = async (type, id) => {
    try {
      const res = await axios.get(`${API_URL}/encyclopedia/${type}/${id}`)
      setSelectedItem({ type, data: res.data })
    } catch (error) {
      console.error('Erreur chargement détails:', error)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
      paddingBottom: '60px',
    }}>
      {/* Header Section */}
      <div style={{
        background: 'linear-gradient(135deg, #DC2626 0%, #DC2626 100%)',
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
          📚 Encyclopédie Automobile Complète
        </h1>
        <p style={{
          fontSize: '18px',
          margin: 0,
          opacity: 0.95,
        }}>
          Base de données exhaustive : marques, modèles, moteurs, transmissions, avis clients
        </p>
      </div>

      <div style={{
        maxWidth: '1400px',
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
              e.target.style.borderColor = '#DC2626'
              e.target.style.boxShadow = '0 0 0 3px rgba(220, 38, 38, 0.1)'
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
            { id: 'brands', label: '🏭 Marques', count: brands.length },
            { id: 'models', label: '🚗 Modèles', count: models.length },
            { id: 'engines', label: '⚙️ Moteurs', count: engines.length },
            { id: 'transmissions', label: '🔧 Boîtes de vitesse', count: transmissions.length },
            { id: 'fuelTypes', label: '⛽ Carburants', count: fuelTypesStats.length },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedCategory(tab.id)}
              style={{
                padding: '12px 24px',
                background: selectedCategory === tab.id ? '#DC2626' : 'white',
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
                  e.target.style.borderColor = '#DC2626'
                }
              }}
              onMouseLeave={(e) => {
                if (selectedCategory !== tab.id) {
                  e.target.style.borderColor = '#E5E7EB'
                }
              }}
            >
              {tab.label} {tab.count > 0 && `(${tab.count})`}
            </button>
          ))}
        </div>

        {/* Loading */}
        {loading && (
          <div style={{ textAlign: 'center', padding: '40px', fontSize: '18px', color: '#6B7280' }}>
            ⏳ Chargement...
          </div>
        )}

        {/* Content */}
        {!loading && (
          <div>
            {/* Brands */}
            {selectedCategory === 'brands' && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                gap: '24px',
              }}>
                {brands.length === 0 && (
                  <div style={{
                    gridColumn: '1 / -1',
                    textAlign: 'center',
                    padding: '40px',
                    fontSize: '18px',
                    color: '#6B7280'
                  }}>
                    Aucune marque trouvée. Lancez le script de peuplement.
                  </div>
                )}
                {brands.map(brand => (
                  <div
                    key={brand.id}
                    style={{
                      background: 'white',
                      borderRadius: '12px',
                      padding: '24px',
                      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                      border: '1px solid #EEEEEE',
                      transition: 'all 0.2s',
                      cursor: 'pointer',
                    }}
                    onClick={() => viewDetails('brands', brand.id)}
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
                      <h3 style={{
                        margin: 0,
                        fontSize: '22px',
                        fontWeight: 700,
                        color: '#222222',
                      }}>
                        {brand.name}
                      </h3>
                    </div>
                    <div style={{
                      fontSize: '13px',
                      color: '#6B7280',
                      marginBottom: '12px',
                    }}>
                      📍 {brand.country} • {brand.market_segment}
                    </div>
                    <p style={{
                      fontSize: '14px',
                      lineHeight: 1.6,
                      color: '#6B7280',
                      marginBottom: '16px',
                    }}>
                      {brand.description?.substring(0, 120)}...
                    </p>
                    <div style={{
                      display: 'flex',
                      gap: '8px',
                      marginBottom: '12px',
                    }}>
                      {brand.reliability_rating && (
                        <span style={{
                          background: '#FEE2E2',
                          color: '#DC2626',
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: 500,
                        }}>
                          ⭐ {brand.reliability_rating}/5
                        </span>
                      )}
                      {brand.reputation_score && (
                        <span style={{
                          background: '#DBEAFE',
                          color: '#1D4ED8',
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: 500,
                        }}>
                          📊 {brand.reputation_score}/100
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Models */}
            {selectedCategory === 'models' && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
                gap: '24px',
              }}>
                {models.length === 0 && (
                  <div style={{
                    gridColumn: '1 / -1',
                    textAlign: 'center',
                    padding: '40px',
                    fontSize: '18px',
                    color: '#6B7280'
                  }}>
                    Aucun modèle trouvé. Lancez le script de peuplement.
                  </div>
                )}
                {models.map(model => (
                  <div
                    key={model.id}
                    style={{
                      background: 'white',
                      borderRadius: '12px',
                      padding: '24px',
                      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                      border: '1px solid #EEEEEE',
                      transition: 'all 0.2s',
                      cursor: 'pointer',
                    }}
                    onClick={() => viewDetails('models', model.id)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)'
                      e.currentTarget.style.boxShadow = '0 12px 40px rgba(0,0,0,0.12)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = '0 1px 2px rgba(0,0,0,0.04)'
                    }}
                  >
                    <h3 style={{
                      margin: '0 0 12px 0',
                      fontSize: '20px',
                      fontWeight: 700,
                      color: '#222222',
                    }}>
                      {model.name}
                    </h3>
                    <div style={{
                      fontSize: '13px',
                      color: '#6B7280',
                      marginBottom: '12px',
                    }}>
                      {model.category} • {model.body_type}
                    </div>
                    <p style={{
                      fontSize: '14px',
                      lineHeight: 1.6,
                      color: '#6B7280',
                      marginBottom: '16px',
                    }}>
                      {model.description?.substring(0, 100)}...
                    </p>
                    <div style={{
                      display: 'flex',
                      gap: '8px',
                      flexWrap: 'wrap',
                    }}>
                      {model.price_new_min && (
                        <span style={{
                          background: '#D1FAE5',
                          color: '#065F46',
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: 500,
                        }}>
                          💰 {model.price_new_min}€+
                        </span>
                      )}
                      {model.safety_rating && (
                        <span style={{
                          background: '#FEE2E2',
                          color: '#DC2626',
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: 500,
                        }}>
                          🛡️ {model.safety_rating}/5
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Engines */}
            {selectedCategory === 'engines' && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
                gap: '24px',
              }}>
                {engines.length === 0 && (
                  <div style={{
                    gridColumn: '1 / -1',
                    textAlign: 'center',
                    padding: '40px',
                    fontSize: '18px',
                    color: '#6B7280'
                  }}>
                    Aucun moteur trouvé. Lancez le script de peuplement.
                  </div>
                )}
                {engines.map(engine => (
                  <div
                    key={engine.id}
                    style={{
                      background: 'white',
                      borderRadius: '12px',
                      padding: '24px',
                      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                      border: '1px solid #EEEEEE',
                      transition: 'all 0.2s',
                      cursor: 'pointer',
                    }}
                    onClick={() => viewDetails('engines', engine.id)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)'
                      e.currentTarget.style.boxShadow = '0 12px 40px rgba(0,0,0,0.12)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = '0 1px 2px rgba(0,0,0,0.04)'
                    }}
                  >
                    <h3 style={{
                      margin: '0 0 12px 0',
                      fontSize: '20px',
                      fontWeight: 700,
                      color: '#222222',
                    }}>
                      {engine.name}
                    </h3>
                    <div style={{
                      fontSize: '13px',
                      color: '#6B7280',
                      marginBottom: '12px',
                    }}>
                      {engine.fuel_type} • {engine.power_hp} ch • {engine.displacement} cm³
                    </div>
                    {engine.description && (
                      <p style={{
                        fontSize: '14px',
                        lineHeight: 1.6,
                        color: '#6B7280',
                        marginBottom: '16px',
                      }}>
                        {engine.description.substring(0, 100)}...
                      </p>
                    )}
                    <div style={{
                      display: 'flex',
                      gap: '8px',
                      flexWrap: 'wrap',
                    }}>
                      {engine.reliability_rating && (
                        <span style={{
                          background: '#FEE2E2',
                          color: '#DC2626',
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: 500,
                        }}>
                          ⭐ {engine.reliability_rating}/5
                        </span>
                      )}
                      {engine.consumption_combined && (
                        <span style={{
                          background: '#D1FAE5',
                          color: '#065F46',
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: 500,
                        }}>
                          ⛽ {engine.consumption_combined}L/100km
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Transmissions */}
            {selectedCategory === 'transmissions' && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                gap: '24px',
              }}>
                {transmissions.length === 0 && (
                  <div style={{
                    gridColumn: '1 / -1',
                    textAlign: 'center',
                    padding: '40px',
                    fontSize: '18px',
                    color: '#6B7280'
                  }}>
                    Aucune transmission trouvée. Lancez le script de peuplement.
                  </div>
                )}
                {transmissions.map(trans => (
                  <div
                    key={trans.id}
                    style={{
                      background: 'white',
                      borderRadius: '12px',
                      padding: '24px',
                      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                      border: '1px solid #EEEEEE',
                      transition: 'all 0.2s',
                      cursor: 'pointer',
                    }}
                    onClick={() => viewDetails('transmissions', trans.id)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)'
                      e.currentTarget.style.boxShadow = '0 12px 40px rgba(0,0,0,0.12)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = '0 1px 2px rgba(0,0,0,0.04)'
                    }}
                  >
                    <h3 style={{
                      margin: '0 0 12px 0',
                      fontSize: '20px',
                      fontWeight: 700,
                      color: '#222222',
                    }}>
                      {trans.name}
                    </h3>
                    <div style={{
                      fontSize: '13px',
                      color: '#6B7280',
                      marginBottom: '12px',
                    }}>
                      {trans.type} • {trans.gears} rapports
                      {trans.manufacturer && ` • ${trans.manufacturer}`}
                    </div>
                    {trans.description && (
                      <p style={{
                        fontSize: '14px',
                        lineHeight: 1.6,
                        color: '#6B7280',
                        marginBottom: '16px',
                      }}>
                        {trans.description.substring(0, 100)}...
                      </p>
                    )}
                    {trans.reliability_rating && (
                      <span style={{
                        background: '#FEE2E2',
                        color: '#DC2626',
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: 500,
                      }}>
                        ⭐ {trans.reliability_rating}/5
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Fuel Types Stats */}
            {selectedCategory === 'fuelTypes' && (
              <div style={{
                maxWidth: '900px',
                margin: '0 auto',
              }}>
                {fuelTypesStats.length === 0 && (
                  <div style={{
                    textAlign: 'center',
                    padding: '40px',
                    fontSize: '18px',
                    color: '#6B7280'
                  }}>
                    Aucune statistique disponible. Lancez le script de peuplement.
                  </div>
                )}
                {fuelTypesStats.map((fuel, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'white',
                      borderRadius: '12px',
                      padding: '24px',
                      marginBottom: '16px',
                      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                      border: '1px solid #EEEEEE',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <h3 style={{
                        margin: '0 0 8px 0',
                        fontSize: '20px',
                        fontWeight: 700,
                        color: '#222222',
                      }}>
                        {fuel.fuel_type}
                      </h3>
                      <p style={{
                        margin: 0,
                        fontSize: '14px',
                        color: '#6B7280',
                      }}>
                        {fuel.count} moteur{fuel.count > 1 ? 's' : ''} disponible{fuel.count > 1 ? 's' : ''}
                      </p>
                    </div>
                    <div style={{
                      background: '#FEE2E2',
                      color: '#DC2626',
                      padding: '12px 24px',
                      borderRadius: '12px',
                      fontSize: '24px',
                      fontWeight: 700,
                    }}>
                      {fuel.count}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Modal Détails */}
        {selectedItem && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0, 0, 0, 0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
              padding: '20px',
            }}
            onClick={() => setSelectedItem(null)}
          >
            <div
              style={{
                background: 'white',
                borderRadius: '16px',
                padding: '32px',
                maxWidth: '800px',
                maxHeight: '80vh',
                overflow: 'auto',
                width: '100%',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '24px',
              }}>
                <h2 style={{
                  margin: 0,
                  fontSize: '28px',
                  fontWeight: 700,
                  color: '#222222',
                }}>
                  {selectedItem.data.name}
                </h2>
                <button
                  onClick={() => setSelectedItem(null)}
                  style={{
                    background: '#F3F4F6',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '8px 16px',
                    cursor: 'pointer',
                    fontSize: '16px',
                    fontWeight: 600,
                  }}
                >
                  ✕ Fermer
                </button>
              </div>

              {/* Contenu du modal selon le type */}
              <div style={{
                fontSize: '15px',
                lineHeight: 1.7,
                color: '#6B7280',
              }}>
                <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                  {JSON.stringify(selectedItem.data, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
