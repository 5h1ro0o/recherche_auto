// frontend/src/components/ProposeVehicleModal.jsx
import React, { useState, useEffect } from 'react'
import { apiPost } from '../services/api'

export default function ProposeVehicleModal({ request, onClose, onSuccess }) {
  const [step, setStep] = useState('search') // 'search' | 'preview' | 'message'
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [selectedVehicle, setSelectedVehicle] = useState(null)
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Templates de messages
  const messageTemplates = [
    {
      id: 'perfect',
      label: '🎯 Correspond parfaitement',
      text: `Ce véhicule correspond parfaitement à vos critères : budget respecté, ${request.preferred_fuel_type || 'motorisation adaptée'}, et ${request.max_mileage ? `faible kilométrage (max ${request.max_mileage} km)` : 'bon état général'}. Je vous le recommande vivement !`
    },
    {
      id: 'excellent',
      label: '⭐ Excellente opportunité',
      text: "Excellent véhicule que je vous recommande : très bon état, entretien suivi, historique complet. C'est une opportunité à ne pas manquer !"
    },
    {
      id: 'value',
      label: '💎 Très bon rapport qualité-prix',
      text: "Ce modèle offre un excellent rapport qualité-prix pour votre budget. Fiabilité reconnue et coûts d'entretien modérés."
    },
    {
      id: 'recent',
      label: '🆕 Modèle récent',
      text: "Véhicule récent avec peu de kilométrage, équipements modernes et garantie constructeur. Parfait pour une utilisation longue durée."
    }
  ]

  // Recherche automatique au chargement basée sur les critères
  useEffect(() => {
    if (request) {
      handleAutoSearch()
    }
  }, [])

  async function handleAutoSearch() {
    setLoading(true)
    setError('')
    
    try {
      const filters = {}
      if (request.budget_max) filters.price_max = request.budget_max
      if (request.preferred_fuel_type) filters.fuel_type = request.preferred_fuel_type
      if (request.preferred_transmission) filters.transmission = request.preferred_transmission
      if (request.max_mileage) filters.mileage_max = request.max_mileage
      if (request.min_year) filters.year_min = request.min_year

      const response = await apiPost('/search', {
        q: searchQuery || null,
        filters,
        page: 1,
        size: 20
      })

      setSearchResults(response.hits || [])
    } catch (err) {
      console.error('Erreur recherche:', err)
      setError('Erreur lors de la recherche')
    } finally {
      setLoading(false)
    }
  }

  async function handleManualSearch() {
    if (!searchQuery.trim()) {
      handleAutoSearch()
      return
    }
    handleAutoSearch()
  }

  function handleSelectVehicle(vehicle) {
    setSelectedVehicle(vehicle)
    setStep('preview')
  }

  function handleUseTemplate(template) {
    setMessage(template.text)
  }

  async function handleSubmit() {
    if (!message.trim()) {
      setError('Veuillez ajouter un message')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await apiPost(`/assisted/requests/${request.id}/propose`, {
        vehicle_id: selectedVehicle.id,
        message: message.trim()
      })

      onSuccess()
    } catch (err) {
      console.error('Erreur proposition:', err)
      setError(err.response?.data?.detail || 'Erreur lors de la proposition')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content large propose-modal" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div>
            <h2>➕ Proposer un véhicule</h2>
            <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#6a737d' }}>
              {step === 'search' && 'Recherchez un véhicule correspondant aux critères'}
              {step === 'preview' && 'Prévisualisez votre proposition'}
              {step === 'message' && 'Personnalisez votre message'}
            </p>
          </div>
          <button onClick={onClose} className="close-modal">✕</button>
        </div>

        {/* Steps indicator */}
        <div style={{ 
          padding: '16px 24px', 
          borderBottom: '1px solid #e1e4e8',
          background: '#f8f9fa'
        }}>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <StepIndicator active={step === 'search'} completed={step !== 'search'}>
              1. Recherche
            </StepIndicator>
            <div style={{ flex: 1, height: '2px', background: '#e1e4e8' }} />
            <StepIndicator active={step === 'preview'} completed={step === 'message'}>
              2. Prévisualisation
            </StepIndicator>
            <div style={{ flex: 1, height: '2px', background: '#e1e4e8' }} />
            <StepIndicator active={step === 'message'}>
              3. Message
            </StepIndicator>
          </div>
        </div>

        {error && (
          <div style={{
            margin: '16px 24px',
            padding: '12px 16px',
            background: '#fee',
            border: '1px solid #fcc',
            borderRadius: '8px',
            color: '#c33',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}

        {/* Content */}
        <div style={{ padding: '24px', maxHeight: 'calc(90vh - 300px)', overflowY: 'auto' }}>
          {/* STEP 1: Search */}
          {step === 'search' && (
            <SearchStep
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
              searchResults={searchResults}
              loading={loading}
              onSearch={handleManualSearch}
              onSelect={handleSelectVehicle}
              requestCriteria={request}
            />
          )}

          {/* STEP 2: Preview */}
          {step === 'preview' && selectedVehicle && (
            <PreviewStep
              vehicle={selectedVehicle}
              request={request}
              onBack={() => setStep('search')}
              onNext={() => setStep('message')}
            />
          )}

          {/* STEP 3: Message */}
          {step === 'message' && selectedVehicle && (
            <MessageStep
              vehicle={selectedVehicle}
              message={message}
              setMessage={setMessage}
              templates={messageTemplates}
              onUseTemplate={handleUseTemplate}
              onBack={() => setStep('preview')}
              onSubmit={handleSubmit}
              loading={loading}
            />
          )}
        </div>
      </div>
    </div>
  )
}

// ============ STEP COMPONENTS ============

function StepIndicator({ active, completed, children }) {
  return (
    <div style={{
      padding: '8px 16px',
      borderRadius: '20px',
      fontSize: '13px',
      fontWeight: 600,
      background: completed ? '#d4edda' : active ? '#667eea' : '#f0f0f0',
      color: completed ? '#155724' : active ? 'white' : '#6a737d',
      whiteSpace: 'nowrap'
    }}>
      {completed && '✓ '}
      {children}
    </div>
  )
}

function SearchStep({ searchQuery, setSearchQuery, searchResults, loading, onSearch, onSelect, requestCriteria }) {
  return (
    <div>
      {/* Critères du client */}
      <div style={{
        background: '#f6f8ff',
        border: '1px solid #d1e0ff',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '24px'
      }}>
        <strong style={{ display: 'block', marginBottom: '12px', color: '#667eea' }}>
          📋 Critères du client :
        </strong>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '8px',
          fontSize: '13px'
        }}>
          {requestCriteria.budget_max && (
            <div>💰 Budget max : <strong>{requestCriteria.budget_max.toLocaleString()} €</strong></div>
          )}
          {requestCriteria.preferred_fuel_type && (
            <div>⛽ Carburant : <strong>{requestCriteria.preferred_fuel_type}</strong></div>
          )}
          {requestCriteria.preferred_transmission && (
            <div>⚙️ Transmission : <strong>{requestCriteria.preferred_transmission}</strong></div>
          )}
          {requestCriteria.max_mileage && (
            <div>🛣️ Km max : <strong>{requestCriteria.max_mileage.toLocaleString()}</strong></div>
          )}
          {requestCriteria.min_year && (
            <div>📅 Année min : <strong>{requestCriteria.min_year}</strong></div>
          )}
        </div>
      </div>

      {/* Barre de recherche */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && onSearch()}
          placeholder="Affiner la recherche (marque, modèle...)"
          style={{
            flex: 1,
            padding: '12px 16px',
            border: '2px solid #e1e4e8',
            borderRadius: '10px',
            fontSize: '14px'
          }}
        />
        <button
          onClick={onSearch}
          disabled={loading}
          style={{
            padding: '12px 24px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            fontSize: '14px',
            fontWeight: 600,
            cursor: 'pointer',
            whiteSpace: 'nowrap'
          }}
        >
          {loading ? '🔍 Recherche...' : '🔍 Rechercher'}
        </button>
      </div>

      {/* Résultats */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6a737d' }}>
          Recherche en cours...
        </div>
      ) : searchResults.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6a737d' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
          <p>Aucun véhicule trouvé</p>
          <p style={{ fontSize: '13px' }}>Essayez d'ajuster les critères de recherche</p>
        </div>
      ) : (
        <div>
          <div style={{ 
            marginBottom: '12px', 
            fontSize: '14px', 
            color: '#6a737d',
            fontWeight: 500 
          }}>
            {searchResults.length} véhicule(s) trouvé(s)
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '16px'
          }}>
            {searchResults.map(result => (
              <VehicleCard
                key={result.id}
                vehicle={result.source}
                vehicleId={result.id}
                onSelect={() => onSelect({ id: result.id, ...result.source })}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function VehicleCard({ vehicle, vehicleId, onSelect }) {
  return (
    <div style={{
      background: 'white',
      border: '2px solid #e1e4e8',
      borderRadius: '12px',
      padding: '16px',
      transition: 'all 0.2s',
      cursor: 'pointer'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.borderColor = '#667eea'
      e.currentTarget.style.boxShadow = '0 4px 12px rgba(102,126,234,0.15)'
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.borderColor = '#e1e4e8'
      e.currentTarget.style.boxShadow = 'none'
    }}>
      <div style={{
        fontWeight: 600,
        fontSize: '15px',
        marginBottom: '12px',
        color: '#24292e'
      }}>
        {vehicle?.title || 'Véhicule'}
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '8px',
        fontSize: '13px',
        color: '#6a737d',
        marginBottom: '16px'
      }}>
        {vehicle?.price && (
          <div style={{ color: '#28a745', fontWeight: 600 }}>
            💰 {vehicle.price.toLocaleString()} €
          </div>
        )}
        {vehicle?.year && <div>📅 {vehicle.year}</div>}
        {vehicle?.mileage && <div>🛣️ {vehicle.mileage.toLocaleString()} km</div>}
        {vehicle?.fuel_type && <div>⛽ {vehicle.fuel_type}</div>}
      </div>

      <button
        onClick={onSelect}
        style={{
          width: '100%',
          padding: '10px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'transform 0.2s'
        }}
        onMouseEnter={(e) => e.target.style.transform = 'translateY(-2px)'}
        onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
      >
        ➕ Sélectionner ce véhicule
      </button>
    </div>
  )
}

function PreviewStep({ vehicle, request, onBack, onNext }) {
  // Calculer la compatibilité
  const compatibility = calculateCompatibility(vehicle, request)

  return (
    <div>
      <div style={{
        background: 'white',
        border: '2px solid #667eea',
        borderRadius: '16px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h3 style={{ margin: '0 0 20px 0', fontSize: '20px', fontWeight: 700 }}>
          {vehicle.title}
        </h3>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          marginBottom: '20px'
        }}>
          {vehicle.price && (
            <InfoItem label="Prix" value={`${vehicle.price.toLocaleString()} €`} icon="💰" />
          )}
          {vehicle.year && (
            <InfoItem label="Année" value={vehicle.year} icon="📅" />
          )}
          {vehicle.mileage && (
            <InfoItem label="Kilométrage" value={`${vehicle.mileage.toLocaleString()} km`} icon="🛣️" />
          )}
          {vehicle.fuel_type && (
            <InfoItem label="Carburant" value={vehicle.fuel_type} icon="⛽" />
          )}
          {vehicle.transmission && (
            <InfoItem label="Transmission" value={vehicle.transmission} icon="⚙️" />
          )}
        </div>

        {vehicle.description && (
          <div style={{
            background: '#f8f9fa',
            padding: '12px',
            borderRadius: '8px',
            fontSize: '14px',
            lineHeight: 1.6
          }}>
            <strong style={{ display: 'block', marginBottom: '8px' }}>Description :</strong>
            {vehicle.description}
          </div>
        )}
      </div>

      {/* Analyse de compatibilité */}
      <div style={{
        background: compatibility.score >= 80 ? '#d4edda' : compatibility.score >= 60 ? '#fff3cd' : '#fee',
        border: `2px solid ${compatibility.score >= 80 ? '#c3e6cb' : compatibility.score >= 60 ? '#ffc107' : '#fcc'}`,
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <strong style={{ fontSize: '16px' }}>
            📊 Analyse de compatibilité
          </strong>
          <div style={{
            fontSize: '24px',
            fontWeight: 700,
            color: compatibility.score >= 80 ? '#155724' : compatibility.score >= 60 ? '#856404' : '#721c24'
          }}>
            {compatibility.score}%
          </div>
        </div>

        <div style={{ fontSize: '13px', lineHeight: 1.8 }}>
          {compatibility.details.map((detail, idx) => (
            <div key={idx} style={{ marginBottom: '4px' }}>
              {detail.match ? '✓' : '⚠️'} {detail.text}
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: '12px' }}>
        <button
          onClick={onBack}
          style={{
            flex: 1,
            padding: '14px',
            background: 'white',
            border: '2px solid #e1e4e8',
            borderRadius: '10px',
            fontSize: '15px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          ← Retour à la recherche
        </button>
        <button
          onClick={onNext}
          style={{
            flex: 1,
            padding: '14px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            fontSize: '15px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          Continuer vers le message →
        </button>
      </div>
    </div>
  )
}

function InfoItem({ label, value, icon }) {
  return (
    <div>
      <div style={{ fontSize: '12px', color: '#6a737d', marginBottom: '4px' }}>
        {icon} {label}
      </div>
      <div style={{ fontSize: '16px', fontWeight: 600, color: '#24292e' }}>
        {value}
      </div>
    </div>
  )
}

function MessageStep({ vehicle, message, setMessage, templates, onUseTemplate, onBack, onSubmit, loading }) {
  return (
    <div>
      <div style={{
        background: '#f8f9fa',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '24px',
        fontSize: '14px'
      }}>
        <strong style={{ display: 'block', marginBottom: '8px' }}>
          📝 Véhicule sélectionné :
        </strong>
        {vehicle.title}
      </div>

      {/* Templates */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{
          fontSize: '14px',
          fontWeight: 600,
          marginBottom: '12px',
          color: '#24292e'
        }}>
          💬 Messages rapides :
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {templates.map(template => (
            <button
              key={template.id}
              onClick={() => onUseTemplate(template)}
              style={{
                padding: '8px 14px',
                background: '#f0f0f0',
                border: '1px solid #e1e4e8',
                borderRadius: '20px',
                fontSize: '13px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = '#667eea'
                e.target.style.color = 'white'
              }}
              onMouseLeave={(e) => {
                e.target.style.background = '#f0f0f0'
                e.target.style.color = '#24292e'
              }}
            >
              {template.label}
            </button>
          ))}
        </div>
      </div>

      {/* Message personnalisé */}
      <div style={{ marginBottom: '24px' }}>
        <label style={{
          display: 'block',
          fontSize: '14px',
          fontWeight: 600,
          marginBottom: '8px',
          color: '#24292e'
        }}>
          Votre message personnalisé :
        </label>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Expliquez pourquoi ce véhicule correspond aux besoins du client..."
          rows={8}
          style={{
            width: '100%',
            padding: '12px 16px',
            border: '2px solid #e1e4e8',
            borderRadius: '10px',
            fontSize: '14px',
            fontFamily: 'inherit',
            resize: 'vertical'
          }}
        />
        <div style={{
          fontSize: '12px',
          color: '#6a737d',
          marginTop: '6px'
        }}>
          {message.length} caractères
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: '12px' }}>
        <button
          onClick={onBack}
          style={{
            flex: 1,
            padding: '14px',
            background: 'white',
            border: '2px solid #e1e4e8',
            borderRadius: '10px',
            fontSize: '15px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          ← Retour
        </button>
        <button
          onClick={onSubmit}
          disabled={loading || !message.trim()}
          style={{
            flex: 2,
            padding: '14px',
            background: message.trim() ? 'linear-gradient(135deg, #28a745 0%, #20c997 100%)' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            fontSize: '15px',
            fontWeight: 600,
            cursor: message.trim() ? 'pointer' : 'not-allowed'
          }}
        >
          {loading ? '📤 Envoi en cours...' : '✅ Proposer ce véhicule au client'}
        </button>
      </div>
    </div>
  )
}

// ============ HELPER FUNCTIONS ============

function calculateCompatibility(vehicle, request) {
  const details = []
  let score = 0
  let maxScore = 0

  // Prix
  if (request.budget_max) {
    maxScore += 30
    if (vehicle.price && vehicle.price <= request.budget_max) {
      score += 30
      details.push({ match: true, text: `Prix dans le budget (${vehicle.price.toLocaleString()} € ≤ ${request.budget_max.toLocaleString()} €)` })
    } else {
      details.push({ match: false, text: `Prix au-dessus du budget (${vehicle.price?.toLocaleString()} € > ${request.budget_max.toLocaleString()} €)` })
    }
  }

  // Carburant
  if (request.preferred_fuel_type) {
    maxScore += 20
    if (vehicle.fuel_type === request.preferred_fuel_type) {
      score += 20
      details.push({ match: true, text: `Carburant correspondant (${vehicle.fuel_type})` })
    } else {
      details.push({ match: false, text: `Carburant différent (${vehicle.fuel_type} vs ${request.preferred_fuel_type})` })
    }
  }

  // Transmission
  if (request.preferred_transmission) {
    maxScore += 15
    if (vehicle.transmission === request.preferred_transmission) {
      score += 15
      details.push({ match: true, text: `Transmission correspondante (${vehicle.transmission})` })
    } else {
      details.push({ match: false, text: `Transmission différente (${vehicle.transmission} vs ${request.preferred_transmission})` })
    }
  }

  // Kilométrage
  if (request.max_mileage) {
    maxScore += 20
    if (vehicle.mileage && vehicle.mileage <= request.max_mileage) {
      score += 20
      details.push({ match: true, text: `Kilométrage acceptable (${vehicle.mileage.toLocaleString()} km ≤ ${request.max_mileage.toLocaleString()} km)` })
    } else {
      details.push({ match: false, text: `Kilométrage élevé (${vehicle.mileage?.toLocaleString()} km > ${request.max_mileage.toLocaleString()} km)` })
    }
  }

  // Année
  if (request.min_year) {
    maxScore += 15
    if (vehicle.year && vehicle.year >= request.min_year) {
      score += 15
      details.push({ match: true, text: `Année acceptable (${vehicle.year} ≥ ${request.min_year})` })
    } else {
      details.push({ match: false, text: `Véhicule trop ancien (${vehicle.year} < ${request.min_year})` })
    }
  }

  const finalScore = maxScore > 0 ? Math.round((score / maxScore) * 100) : 100

  return {
    score: finalScore,
    details
  }
}