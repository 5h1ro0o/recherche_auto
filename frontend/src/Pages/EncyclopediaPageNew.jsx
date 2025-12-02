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

  // Rendu de la modal de détails selon le type
  const renderDetailModal = () => {
    if (!selectedItem) return null

    const { type, data } = selectedItem

    return (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px',
          backdropFilter: 'blur(4px)',
        }}
        onClick={() => setSelectedItem(null)}
      >
        <div
          style={{
            background: 'white',
            borderRadius: '20px',
            padding: '0',
            maxWidth: '900px',
            maxHeight: '90vh',
            overflow: 'hidden',
            width: '100%',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div style={{
            background: 'linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)',
            color: 'white',
            padding: '32px',
            position: 'relative',
          }}>
            <button
              onClick={() => setSelectedItem(null)}
              style={{
                position: 'absolute',
                top: '16px',
                right: '16px',
                background: 'rgba(255, 255, 255, 0.2)',
                border: 'none',
                borderRadius: '8px',
                padding: '8px 16px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: 600,
                color: 'white',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.3)'
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.2)'
              }}
            >
              ✕ Fermer
            </button>
            <h2 style={{
              margin: '0 0 8px 0',
              fontSize: '32px',
              fontWeight: 700,
            }}>
              {data.name}
            </h2>
            {type === 'brands' && data.country && (
              <p style={{ margin: 0, fontSize: '16px', opacity: 0.9 }}>
                📍 {data.country} • {data.market_segment}
              </p>
            )}
          </div>

          {/* Content */}
          <div style={{
            padding: '32px',
            maxHeight: 'calc(90vh - 140px)',
            overflowY: 'auto',
          }}>
            {type === 'brands' && <BrandDetails data={data} />}
            {type === 'models' && <ModelDetails data={data} />}
            {type === 'engines' && <EngineDetails data={data} />}
            {type === 'transmissions' && <TransmissionDetails data={data} />}
          </div>
        </div>
      </div>
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
        background: 'linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)',
        color: 'white',
        padding: '60px 20px',
        textAlign: 'center',
        marginBottom: '40px',
        boxShadow: '0 10px 40px rgba(220, 38, 38, 0.2)',
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
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#DC2626'
              e.target.style.boxShadow = '0 0 0 3px rgba(220, 38, 38, 0.1), 0 2px 8px rgba(0,0,0,0.04)'
            }}
            onBlur={(e) => {
              e.target.style.borderColor = '#E5E7EB'
              e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.04)'
            }}
          />
        </div>

        {/* Category Tabs */}
        <div style={{
          display: 'flex',
          gap: '12px',
          marginBottom: '40px',
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
                background: selectedCategory === tab.id ? 'linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)' : 'white',
                color: selectedCategory === tab.id ? 'white' : '#222222',
                border: selectedCategory === tab.id ? 'none' : '2px solid #E5E7EB',
                borderRadius: '12px',
                fontSize: '15px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s',
                boxShadow: selectedCategory === tab.id ? '0 4px 12px rgba(220, 38, 38, 0.3)' : '0 2px 4px rgba(0,0,0,0.04)',
              }}
              onMouseEnter={(e) => {
                if (selectedCategory !== tab.id) {
                  e.target.style.borderColor = '#DC2626'
                  e.target.style.transform = 'translateY(-2px)'
                  e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)'
                }
              }}
              onMouseLeave={(e) => {
                if (selectedCategory !== tab.id) {
                  e.target.style.borderColor = '#E5E7EB'
                  e.target.style.transform = 'translateY(0)'
                  e.target.style.boxShadow = '0 2px 4px rgba(0,0,0,0.04)'
                }
              }}
            >
              {tab.label} {tab.count > 0 && `(${tab.count})`}
            </button>
          ))}
        </div>

        {/* Loading */}
        {loading && (
          <div style={{ textAlign: 'center', padding: '60px', fontSize: '18px', color: '#6B7280' }}>
            <div style={{
              display: 'inline-block',
              width: '48px',
              height: '48px',
              border: '4px solid #E5E7EB',
              borderTop: '4px solid #DC2626',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
            }} />
            <p style={{ marginTop: '16px' }}>⏳ Chargement...</p>
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
                    padding: '60px 20px',
                    background: 'white',
                    borderRadius: '16px',
                    border: '2px dashed #E5E7EB',
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>🏭</div>
                    <div style={{ fontSize: '18px', fontWeight: 600, color: '#222', marginBottom: '8px' }}>
                      Aucune marque trouvée
                    </div>
                    <div style={{ fontSize: '14px', color: '#6B7280' }}>
                      Lancez le script de peuplement pour ajouter des données
                    </div>
                  </div>
                )}
                {brands.map(brand => (
                  <div
                    key={brand.id}
                    style={{
                      background: 'white',
                      borderRadius: '16px',
                      padding: '24px',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                      border: '1px solid #F3F4F6',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      cursor: 'pointer',
                    }}
                    onClick={() => viewDetails('brands', brand.id)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-8px)'
                      e.currentTarget.style.boxShadow = '0 20px 40px rgba(220, 38, 38, 0.15)'
                      e.currentTarget.style.borderColor = '#DC2626'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)'
                      e.currentTarget.style.borderColor = '#F3F4F6'
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      marginBottom: '16px',
                    }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        background: 'linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '24px',
                      }}>
                        🏭
                      </div>
                      <h3 style={{
                        margin: 0,
                        fontSize: '22px',
                        fontWeight: 700,
                        color: '#222222',
                        flex: 1,
                      }}>
                        {brand.name}
                      </h3>
                    </div>
                    <div style={{
                      fontSize: '13px',
                      color: '#6B7280',
                      marginBottom: '12px',
                      fontWeight: 500,
                    }}>
                      📍 {brand.country} • {brand.market_segment}
                    </div>
                    <p style={{
                      fontSize: '14px',
                      lineHeight: 1.6,
                      color: '#6B7280',
                      marginBottom: '16px',
                      minHeight: '60px',
                    }}>
                      {brand.description?.substring(0, 120)}...
                    </p>
                    <div style={{
                      display: 'flex',
                      gap: '8px',
                      flexWrap: 'wrap',
                    }}>
                      {brand.reliability_rating && (
                        <span style={{
                          background: 'linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)',
                          color: '#DC2626',
                          padding: '6px 14px',
                          borderRadius: '20px',
                          fontSize: '12px',
                          fontWeight: 600,
                        }}>
                          ⭐ {brand.reliability_rating}/5
                        </span>
                      )}
                      {brand.reputation_score && (
                        <span style={{
                          background: 'linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)',
                          color: '#1D4ED8',
                          padding: '6px 14px',
                          borderRadius: '20px',
                          fontSize: '12px',
                          fontWeight: 600,
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
                    padding: '60px 20px',
                    background: 'white',
                    borderRadius: '16px',
                    border: '2px dashed #E5E7EB',
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>🚗</div>
                    <div style={{ fontSize: '18px', fontWeight: 600, color: '#222', marginBottom: '8px' }}>
                      Aucun modèle trouvé
                    </div>
                    <div style={{ fontSize: '14px', color: '#6B7280' }}>
                      Lancez le script de peuplement pour ajouter des données
                    </div>
                  </div>
                )}
                {models.map(model => (
                  <div
                    key={model.id}
                    style={{
                      background: 'white',
                      borderRadius: '16px',
                      padding: '24px',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                      border: '1px solid #F3F4F6',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      cursor: 'pointer',
                    }}
                    onClick={() => viewDetails('models', model.id)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-8px)'
                      e.currentTarget.style.boxShadow = '0 20px 40px rgba(220, 38, 38, 0.15)'
                      e.currentTarget.style.borderColor = '#DC2626'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)'
                      e.currentTarget.style.borderColor = '#F3F4F6'
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      marginBottom: '12px',
                    }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        background: 'linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '24px',
                      }}>
                        🚗
                      </div>
                      <h3 style={{
                        margin: 0,
                        fontSize: '20px',
                        fontWeight: 700,
                        color: '#222222',
                        flex: 1,
                      }}>
                        {model.name}
                      </h3>
                    </div>
                    <div style={{
                      fontSize: '13px',
                      color: '#6B7280',
                      marginBottom: '12px',
                      fontWeight: 500,
                    }}>
                      {model.category} • {model.body_type}
                    </div>
                    <p style={{
                      fontSize: '14px',
                      lineHeight: 1.6,
                      color: '#6B7280',
                      marginBottom: '16px',
                      minHeight: '60px',
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
                          background: 'linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)',
                          color: '#065F46',
                          padding: '6px 14px',
                          borderRadius: '20px',
                          fontSize: '12px',
                          fontWeight: 600,
                        }}>
                          💰 {model.price_new_min}€+
                        </span>
                      )}
                      {model.safety_rating && (
                        <span style={{
                          background: 'linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)',
                          color: '#DC2626',
                          padding: '6px 14px',
                          borderRadius: '20px',
                          fontSize: '12px',
                          fontWeight: 600,
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
                    padding: '60px 20px',
                    background: 'white',
                    borderRadius: '16px',
                    border: '2px dashed #E5E7EB',
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚙️</div>
                    <div style={{ fontSize: '18px', fontWeight: 600, color: '#222', marginBottom: '8px' }}>
                      Aucun moteur trouvé
                    </div>
                    <div style={{ fontSize: '14px', color: '#6B7280' }}>
                      Lancez le script de peuplement pour ajouter des données
                    </div>
                  </div>
                )}
                {engines.map(engine => (
                  <div
                    key={engine.id}
                    style={{
                      background: 'white',
                      borderRadius: '16px',
                      padding: '24px',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                      border: '1px solid #F3F4F6',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      cursor: 'pointer',
                    }}
                    onClick={() => viewDetails('engines', engine.id)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-8px)'
                      e.currentTarget.style.boxShadow = '0 20px 40px rgba(220, 38, 38, 0.15)'
                      e.currentTarget.style.borderColor = '#DC2626'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)'
                      e.currentTarget.style.borderColor = '#F3F4F6'
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      marginBottom: '12px',
                    }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        background: 'linear-gradient(135deg, #FCE7F3 0%, #FBCFE8 100%)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '24px',
                      }}>
                        ⚙️
                      </div>
                      <h3 style={{
                        margin: 0,
                        fontSize: '20px',
                        fontWeight: 700,
                        color: '#222222',
                        flex: 1,
                      }}>
                        {engine.name}
                      </h3>
                    </div>
                    <div style={{
                      fontSize: '13px',
                      color: '#6B7280',
                      marginBottom: '12px',
                      fontWeight: 500,
                    }}>
                      {engine.fuel_type} • {engine.power_hp} ch • {engine.displacement} cm³
                    </div>
                    {engine.description && (
                      <p style={{
                        fontSize: '14px',
                        lineHeight: 1.6,
                        color: '#6B7280',
                        marginBottom: '16px',
                        minHeight: '60px',
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
                          background: 'linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)',
                          color: '#DC2626',
                          padding: '6px 14px',
                          borderRadius: '20px',
                          fontSize: '12px',
                          fontWeight: 600,
                        }}>
                          ⭐ {engine.reliability_rating}/5
                        </span>
                      )}
                      {engine.consumption_combined && (
                        <span style={{
                          background: 'linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)',
                          color: '#065F46',
                          padding: '6px 14px',
                          borderRadius: '20px',
                          fontSize: '12px',
                          fontWeight: 600,
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
                    padding: '60px 20px',
                    background: 'white',
                    borderRadius: '16px',
                    border: '2px dashed #E5E7EB',
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔧</div>
                    <div style={{ fontSize: '18px', fontWeight: 600, color: '#222', marginBottom: '8px' }}>
                      Aucune transmission trouvée
                    </div>
                    <div style={{ fontSize: '14px', color: '#6B7280' }}>
                      Lancez le script de peuplement pour ajouter des données
                    </div>
                  </div>
                )}
                {transmissions.map(trans => (
                  <div
                    key={trans.id}
                    style={{
                      background: 'white',
                      borderRadius: '16px',
                      padding: '24px',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                      border: '1px solid #F3F4F6',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      cursor: 'pointer',
                    }}
                    onClick={() => viewDetails('transmissions', trans.id)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-8px)'
                      e.currentTarget.style.boxShadow = '0 20px 40px rgba(220, 38, 38, 0.15)'
                      e.currentTarget.style.borderColor = '#DC2626'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)'
                      e.currentTarget.style.borderColor = '#F3F4F6'
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      marginBottom: '12px',
                    }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        background: 'linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '24px',
                      }}>
                        🔧
                      </div>
                      <h3 style={{
                        margin: 0,
                        fontSize: '20px',
                        fontWeight: 700,
                        color: '#222222',
                        flex: 1,
                      }}>
                        {trans.name}
                      </h3>
                    </div>
                    <div style={{
                      fontSize: '13px',
                      color: '#6B7280',
                      marginBottom: '12px',
                      fontWeight: 500,
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
                        minHeight: '60px',
                      }}>
                        {trans.description.substring(0, 100)}...
                      </p>
                    )}
                    {trans.reliability_rating && (
                      <span style={{
                        background: 'linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)',
                        color: '#DC2626',
                        padding: '6px 14px',
                        borderRadius: '20px',
                        fontSize: '12px',
                        fontWeight: 600,
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
                    padding: '60px 20px',
                    background: 'white',
                    borderRadius: '16px',
                    border: '2px dashed #E5E7EB',
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>⛽</div>
                    <div style={{ fontSize: '18px', fontWeight: 600, color: '#222', marginBottom: '8px' }}>
                      Aucune statistique disponible
                    </div>
                    <div style={{ fontSize: '14px', color: '#6B7280' }}>
                      Lancez le script de peuplement pour ajouter des données
                    </div>
                  </div>
                )}
                {fuelTypesStats.map((fuel, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'white',
                      borderRadius: '16px',
                      padding: '24px',
                      marginBottom: '16px',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                      border: '1px solid #F3F4F6',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      transition: 'all 0.2s',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)'
                      e.currentTarget.style.transform = 'translateY(-2px)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)'
                      e.currentTarget.style.transform = 'translateY(0)'
                    }}
                  >
                    <div>
                      <h3 style={{
                        margin: '0 0 8px 0',
                        fontSize: '20px',
                        fontWeight: 700,
                        color: '#222222',
                      }}>
                        ⛽ {fuel.fuel_type}
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
                      background: 'linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)',
                      color: '#DC2626',
                      padding: '16px 28px',
                      borderRadius: '16px',
                      fontSize: '28px',
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
        {renderDetailModal()}
      </div>

      {/* Add keyframes for loading animation */}
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  )
}

// Composants de détails
function BrandDetails({ data }) {
  return (
    <div>
      {/* Description */}
      <Section title="📝 Description">
        <p style={{ fontSize: '15px', lineHeight: 1.8, color: '#374151', margin: 0 }}>
          {data.description || 'Aucune description disponible'}
        </p>
      </Section>

      {/* Informations générales */}
      <Section title="ℹ️ Informations générales">
        <InfoGrid>
          <InfoItem label="Pays d'origine" value={data.country} />
          <InfoItem label="Segment de marché" value={data.market_segment} />
          <InfoItem label="Année de fondation" value={data.year_founded} />
          <InfoItem label="Site web" value={data.website} link />
        </InfoGrid>
      </Section>

      {/* Évaluations */}
      <Section title="⭐ Évaluations">
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          {data.reliability_rating && (
            <Badge color="red">
              ⭐ Fiabilité : {data.reliability_rating}/5
            </Badge>
          )}
          {data.reputation_score && (
            <Badge color="blue">
              📊 Réputation : {data.reputation_score}/100
            </Badge>
          )}
        </div>
      </Section>

      {/* Points forts et faibles */}
      {(data.strengths || data.weaknesses) && (
        <Section title="⚖️ Points forts et faibles">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            {data.strengths && (
              <div>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: 600, color: '#065F46' }}>
                  ✅ Points forts
                </h4>
                <ul style={{ margin: 0, paddingLeft: '20px', color: '#374151' }}>
                  {data.strengths.split(',').map((strength, idx) => (
                    <li key={idx} style={{ marginBottom: '8px' }}>{strength.trim()}</li>
                  ))}
                </ul>
              </div>
            )}
            {data.weaknesses && (
              <div>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: 600, color: '#DC2626' }}>
                  ⚠️ Points faibles
                </h4>
                <ul style={{ margin: 0, paddingLeft: '20px', color: '#374151' }}>
                  {data.weaknesses.split(',').map((weakness, idx) => (
                    <li key={idx} style={{ marginBottom: '8px' }}>{weakness.trim()}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Section>
      )}
    </div>
  )
}

function ModelDetails({ data }) {
  return (
    <div>
      {/* Description */}
      <Section title="📝 Description">
        <p style={{ fontSize: '15px', lineHeight: 1.8, color: '#374151', margin: 0 }}>
          {data.description || 'Aucune description disponible'}
        </p>
      </Section>

      {/* Caractéristiques générales */}
      <Section title="🚗 Caractéristiques générales">
        <InfoGrid>
          <InfoItem label="Catégorie" value={data.category} />
          <InfoItem label="Type de carrosserie" value={data.body_type} />
          <InfoItem label="Années de production" value={data.production_years} />
          <InfoItem label="Nombre de places" value={data.seats} />
          <InfoItem label="Nombre de portes" value={data.doors} />
        </InfoGrid>
      </Section>

      {/* Prix */}
      {(data.price_new_min || data.price_used_avg) && (
        <Section title="💰 Prix">
          <InfoGrid>
            <InfoItem label="Prix neuf (min)" value={data.price_new_min ? `${data.price_new_min}€` : null} />
            <InfoItem label="Prix neuf (max)" value={data.price_new_max ? `${data.price_new_max}€` : null} />
            <InfoItem label="Prix occasion (moyen)" value={data.price_used_avg ? `${data.price_used_avg}€` : null} />
          </InfoGrid>
        </Section>
      )}

      {/* Performances */}
      <Section title="⚡ Performances">
        <InfoGrid>
          <InfoItem label="Vitesse max" value={data.top_speed_kmh ? `${data.top_speed_kmh} km/h` : null} />
          <InfoItem label="0-100 km/h" value={data.acceleration_0_100 ? `${data.acceleration_0_100}s` : null} />
        </InfoGrid>
      </Section>

      {/* Dimensions */}
      {(data.length_mm || data.width_mm || data.height_mm) && (
        <Section title="📏 Dimensions">
          <InfoGrid>
            <InfoItem label="Longueur" value={data.length_mm ? `${data.length_mm} mm` : null} />
            <InfoItem label="Largeur" value={data.width_mm ? `${data.width_mm} mm` : null} />
            <InfoItem label="Hauteur" value={data.height_mm ? `${data.height_mm} mm` : null} />
            <InfoItem label="Empattement" value={data.wheelbase_mm ? `${data.wheelbase_mm} mm` : null} />
            <InfoItem label="Volume coffre" value={data.trunk_volume_l ? `${data.trunk_volume_l} L` : null} />
          </InfoGrid>
        </Section>
      )}

      {/* Évaluations */}
      {(data.safety_rating || data.comfort_rating) && (
        <Section title="⭐ Évaluations">
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            {data.safety_rating && (
              <Badge color="red">
                🛡️ Sécurité : {data.safety_rating}/5
              </Badge>
            )}
            {data.comfort_rating && (
              <Badge color="blue">
                🪑 Confort : {data.comfort_rating}/5
              </Badge>
            )}
            {data.reliability_rating && (
              <Badge color="green">
                ⭐ Fiabilité : {data.reliability_rating}/5
              </Badge>
            )}
          </div>
        </Section>
      )}

      {/* Avis */}
      {(data.review_summary_positive || data.review_summary_negative) && (
        <Section title="💬 Avis">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            {data.review_summary_positive && (
              <div>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: 600, color: '#065F46' }}>
                  ✅ Avis positifs
                </h4>
                <p style={{ margin: 0, fontSize: '14px', lineHeight: 1.6, color: '#374151' }}>
                  {data.review_summary_positive}
                </p>
              </div>
            )}
            {data.review_summary_negative && (
              <div>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: 600, color: '#DC2626' }}>
                  ⚠️ Avis négatifs
                </h4>
                <p style={{ margin: 0, fontSize: '14px', lineHeight: 1.6, color: '#374151' }}>
                  {data.review_summary_negative}
                </p>
              </div>
            )}
          </div>
        </Section>
      )}
    </div>
  )
}

function EngineDetails({ data }) {
  return (
    <div>
      {/* Description */}
      {data.description && (
        <Section title="📝 Description">
          <p style={{ fontSize: '15px', lineHeight: 1.8, color: '#374151', margin: 0 }}>
            {data.description}
          </p>
        </Section>
      )}

      {/* Caractéristiques techniques */}
      <Section title="⚙️ Caractéristiques techniques">
        <InfoGrid>
          <InfoItem label="Type de carburant" value={data.fuel_type} />
          <InfoItem label="Puissance" value={data.power_hp ? `${data.power_hp} ch` : null} />
          <InfoItem label="Couple" value={data.torque_nm ? `${data.torque_nm} Nm` : null} />
          <InfoItem label="Cylindrée" value={data.displacement ? `${data.displacement} cm³` : null} />
          <InfoItem label="Architecture" value={data.architecture} />
          <InfoItem label="Nombre de cylindres" value={data.cylinders} />
          <InfoItem label="Turbo" value={data.turbo ? 'Oui' : 'Non'} />
        </InfoGrid>
      </Section>

      {/* Consommation et émissions */}
      {(data.consumption_combined || data.co2_emissions) && (
        <Section title="⛽ Consommation et émissions">
          <InfoGrid>
            <InfoItem label="Consommation mixte" value={data.consumption_combined ? `${data.consumption_combined} L/100km` : null} />
            <InfoItem label="Consommation urbaine" value={data.consumption_urban ? `${data.consumption_urban} L/100km` : null} />
            <InfoItem label="Consommation extra-urbaine" value={data.consumption_highway ? `${data.consumption_highway} L/100km` : null} />
            <InfoItem label="Émissions CO2" value={data.co2_emissions ? `${data.co2_emissions} g/km` : null} />
          </InfoGrid>
        </Section>
      )}

      {/* Fiabilité */}
      {data.reliability_rating && (
        <Section title="⭐ Fiabilité">
          <Badge color="red">
            ⭐ Note de fiabilité : {data.reliability_rating}/5
          </Badge>
          {data.common_issues && (
            <div style={{ marginTop: '16px' }}>
              <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: 600, color: '#DC2626' }}>
                ⚠️ Problèmes courants
              </h4>
              <p style={{ margin: 0, fontSize: '14px', lineHeight: 1.6, color: '#374151' }}>
                {data.common_issues}
              </p>
            </div>
          )}
        </Section>
      )}
    </div>
  )
}

function TransmissionDetails({ data }) {
  return (
    <div>
      {/* Description */}
      {data.description && (
        <Section title="📝 Description">
          <p style={{ fontSize: '15px', lineHeight: 1.8, color: '#374151', margin: 0 }}>
            {data.description}
          </p>
        </Section>
      )}

      {/* Caractéristiques techniques */}
      <Section title="🔧 Caractéristiques techniques">
        <InfoGrid>
          <InfoItem label="Type" value={data.type} />
          <InfoItem label="Nombre de rapports" value={data.gears} />
          <InfoItem label="Fabricant" value={data.manufacturer} />
          <InfoItem label="Code interne" value={data.code} />
        </InfoGrid>
      </Section>

      {/* Fiabilité */}
      {data.reliability_rating && (
        <Section title="⭐ Fiabilité">
          <Badge color="red">
            ⭐ Note de fiabilité : {data.reliability_rating}/5
          </Badge>
          {data.common_issues && (
            <div style={{ marginTop: '16px' }}>
              <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: 600, color: '#DC2626' }}>
                ⚠️ Problèmes courants
              </h4>
              <p style={{ margin: 0, fontSize: '14px', lineHeight: 1.6, color: '#374151' }}>
                {data.common_issues}
              </p>
            </div>
          )}
        </Section>
      )}

      {/* Retours utilisateurs */}
      {data.user_feedback && (
        <Section title="💬 Retours utilisateurs">
          <p style={{ margin: 0, fontSize: '14px', lineHeight: 1.6, color: '#374151' }}>
            {data.user_feedback}
          </p>
        </Section>
      )}
    </div>
  )
}

// Composants utilitaires
function Section({ title, children }) {
  return (
    <div style={{ marginBottom: '32px' }}>
      <h3 style={{
        margin: '0 0 16px 0',
        fontSize: '18px',
        fontWeight: 700,
        color: '#111827',
        paddingBottom: '12px',
        borderBottom: '2px solid #F3F4F6',
      }}>
        {title}
      </h3>
      {children}
    </div>
  )
}

function InfoGrid({ children }) {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: '16px',
    }}>
      {children}
    </div>
  )
}

function InfoItem({ label, value, link }) {
  if (!value) return null

  return (
    <div style={{
      background: '#F9FAFB',
      padding: '16px',
      borderRadius: '12px',
      border: '1px solid #E5E7EB',
    }}>
      <div style={{
        fontSize: '12px',
        fontWeight: 600,
        color: '#6B7280',
        marginBottom: '6px',
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
      }}>
        {label}
      </div>
      {link ? (
        <a
          href={value.startsWith('http') ? value : `https://${value}`}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            fontSize: '15px',
            fontWeight: 600,
            color: '#DC2626',
            textDecoration: 'none',
          }}
        >
          {value}
        </a>
      ) : (
        <div style={{
          fontSize: '15px',
          fontWeight: 600,
          color: '#111827',
        }}>
          {value}
        </div>
      )}
    </div>
  )
}

function Badge({ color, children }) {
  const colors = {
    red: { bg: 'linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)', text: '#DC2626' },
    blue: { bg: 'linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)', text: '#1D4ED8' },
    green: { bg: 'linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)', text: '#065F46' },
  }

  const style = colors[color] || colors.red

  return (
    <span style={{
      display: 'inline-block',
      background: style.bg,
      color: style.text,
      padding: '8px 18px',
      borderRadius: '20px',
      fontSize: '14px',
      fontWeight: 600,
    }}>
      {children}
    </span>
  )
}
