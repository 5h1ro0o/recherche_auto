// frontend/src/Pages/ExpertRequestDetailPage.jsx
// Route à ajouter dans frontend/src/main.jsx :
// <Route path="/expert/request/:requestId" element={<ProtectedRoute requiredRole="EXPERT"><ExpertRequestDetailPage /></ProtectedRoute>} />

import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import useSWR from 'swr'
import {
  getRequestDetail,
  getMyProposals,
  proposeVehicle,
  completeRequest
} from '../services/assisted'
import { apiPost } from '../services/api'

export default function ExpertRequestDetailPage() {
  const { requestId } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  
  const [showProposeModal, setShowProposeModal] = useState(false)
  const [showSearchModal, setShowSearchModal] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searchLoading, setSearchLoading] = useState(false)

  // Charger la demande et les propositions existantes
  const { data: request, mutate: mutateRequest } = useSWR(
    requestId ? `/assisted/expert/request/${requestId}` : null,
    () => getRequestDetail(requestId)
  )

  const { data: proposals, mutate: mutateProposals } = useSWR(
    requestId ? `/assisted/expert/proposals/${requestId}` : null,
    () => getMyProposals(requestId)
  )

  if (!request) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Chargement...</div>
  }

  async function handleSearchVehicles() {
    setSearchLoading(true)
    try {
      // Construire les filtres basés sur les critères de la demande
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
      setShowSearchModal(true)
    } catch (error) {
      console.error('Erreur recherche:', error)
      alert('❌ Erreur lors de la recherche')
    } finally {
      setSearchLoading(false)
    }
  }

  async function handleProposeVehicle(vehicleId, message) {
    try {
      await proposeVehicle(requestId, vehicleId, message)
      mutateProposals()
      setShowProposeModal(false)
      setShowSearchModal(false)
      alert('✅ Véhicule proposé avec succès !')
    } catch (error) {
      console.error('Erreur:', error)
      alert('❌ Erreur lors de la proposition')
    }
  }

  async function handleComplete() {
    if (!confirm('Marquer cette demande comme terminée ?')) return
    
    try {
      await completeRequest(requestId)
      mutateRequest()
      alert('✅ Demande terminée')
      navigate('/expert')
    } catch (error) {
      console.error('Erreur:', error)
      alert('❌ Erreur')
    }
  }

  const stats = {
    proposed: proposals?.length || 0,
    favorites: proposals?.filter(p => p.status === 'FAVORITE').length || 0,
    rejected: proposals?.filter(p => p.status === 'REJECTED').length || 0,
    pending: proposals?.filter(p => p.status === 'PENDING').length || 0
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '20px' }}>
      {/* Header */}
      <div style={{ marginBottom: '30px' }}>
        <button 
          onClick={() => navigate('/expert')}
          style={{
            background: 'none',
            border: '1px solid #ddd',
            padding: '8px 16px',
            borderRadius: '8px',
            cursor: 'pointer',
            marginBottom: '16px'
          }}
        >
          ← Retour au dashboard
        </button>
        
        <RequestCard request={request} />
      </div>

      {/* KPIs */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '30px'
      }}>
        <StatCard icon="📋" label="Propositions" value={stats.proposed} color="#667eea" />
        <StatCard icon="❤️" label="Coup de cœur" value={stats.favorites} color="#e91e63" />
        <StatCard icon="⏱️" label="En attente" value={stats.pending} color="#ffc107" />
        <StatCard icon="❌" label="Refusés" value={stats.rejected} color="#dc3545" />
      </div>

      {/* Actions principales */}
      <div style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '30px',
        flexWrap: 'wrap'
      }}>
        <button
          onClick={handleSearchVehicles}
          disabled={searchLoading}
          style={{
            flex: '1',
            minWidth: '200px',
            padding: '14px 24px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            fontSize: '15px',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.3s'
          }}
        >
          {searchLoading ? '🔍 Recherche...' : '🔍 Rechercher des véhicules'}
        </button>

        <button
          onClick={handleComplete}
          disabled={request.status === 'TERMINEE'}
          style={{
            padding: '14px 24px',
            background: request.status === 'TERMINEE' ? '#ccc' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            fontSize: '15px',
            fontWeight: 600,
            cursor: request.status === 'TERMINEE' ? 'not-allowed' : 'pointer'
          }}
        >
          ✅ Terminer la demande
        </button>
      </div>

      {/* Propositions existantes */}
      <div>
        <h2 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '20px' }}>
          Véhicules proposés ({proposals?.length || 0})
        </h2>

        {!proposals || proposals.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            background: 'white',
            borderRadius: '12px',
            color: '#6a737d'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🚗</div>
            <p>Aucun véhicule proposé pour le moment</p>
            <p>Utilisez le bouton "Rechercher" ci-dessus</p>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
            gap: '20px'
          }}>
            {proposals.map(proposal => (
              <ProposalCard
                key={proposal.id}
                proposal={proposal}
                onViewVehicle={(id) => window.open(`/vehicle/${id}`, '_blank')}
              />
            ))}
          </div>
        )}
      </div>

      {/* Modal recherche véhicules */}
      {showSearchModal && (
        <SearchResultsModal
          results={searchResults}
          onClose={() => setShowSearchModal(false)}
          onPropose={(vehicleId) => {
            setShowProposeModal(vehicleId)
          }}
          alreadyProposedIds={proposals?.map(p => p.vehicle_id) || []}
        />
      )}

      {/* Modal proposition */}
      {showProposeModal && (
        <ProposeVehicleModal
          vehicleId={showProposeModal}
          requestCriteria={request}
          onClose={() => setShowProposeModal(false)}
          onConfirm={(message) => handleProposeVehicle(showProposeModal, message)}
        />
      )}
    </div>
  )
}

function RequestCard({ request }) {
  const getStatusBadge = (status) => {
    const badges = {
      'EN_ATTENTE': { text: '⏳ En attente', color: '#ffc107' },
      'EN_COURS': { text: '🔄 En cours', color: '#17a2b8' },
      'TERMINEE': { text: '✅ Terminée', color: '#28a745' }
    }
    const badge = badges[status] || badges['EN_COURS']
    return (
      <span style={{
        background: badge.color,
        color: 'white',
        padding: '6px 14px',
        borderRadius: '20px',
        fontSize: '13px',
        fontWeight: 600
      }}>
        {badge.text}
      </span>
    )
  }

  return (
    <div style={{
      background: 'white',
      padding: '24px',
      borderRadius: '16px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '20px'
      }}>
        <div>
          <h1 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: 700 }}>
            Demande de {request.client?.full_name || request.client?.email}
          </h1>
          <p style={{ color: '#6a737d', margin: 0, fontSize: '14px' }}>
            Créée le {new Date(request.created_at).toLocaleDateString('fr-FR')}
          </p>
        </div>
        {getStatusBadge(request.status)}
      </div>

      <div style={{
        background: '#f8f9fa',
        padding: '16px',
        borderRadius: '12px',
        marginBottom: '20px'
      }}>
        <strong style={{ display: 'block', marginBottom: '8px', color: '#24292e' }}>
          📝 Description :
        </strong>
        <p style={{ margin: 0, lineHeight: 1.6, color: '#586069' }}>
          {request.description}
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px'
      }}>
        {request.budget_max && (
          <CriteriaItem
            label="Budget max"
            value={`${request.budget_max.toLocaleString()} €`}
            icon="💰"
            color="#28a745"
          />
        )}
        {request.preferred_fuel_type && (
          <CriteriaItem
            label="Carburant"
            value={request.preferred_fuel_type}
            icon="⛽"
          />
        )}
        {request.preferred_transmission && (
          <CriteriaItem
            label="Transmission"
            value={request.preferred_transmission}
            icon="⚙️"
          />
        )}
        {request.max_mileage && (
          <CriteriaItem
            label="Km max"
            value={`${request.max_mileage.toLocaleString()} km`}
            icon="🛣️"
          />
        )}
        {request.min_year && (
          <CriteriaItem
            label="Année min"
            value={request.min_year}
            icon="📅"
          />
        )}
      </div>
    </div>
  )
}

function CriteriaItem({ label, value, icon, color = '#24292e' }) {
  return (
    <div>
      <div style={{ fontSize: '12px', color: '#6a737d', marginBottom: '4px' }}>
        {icon} {label}
      </div>
      <div style={{ fontSize: '18px', fontWeight: 600, color }}>
        {value}
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, color }) {
  return (
    <div style={{
      background: 'white',
      padding: '20px',
      borderRadius: '12px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      display: 'flex',
      alignItems: 'center',
      gap: '16px'
    }}>
      <div style={{ fontSize: '40px', lineHeight: 1 }}>{icon}</div>
      <div>
        <div style={{
          fontSize: '12px',
          color: '#6a737d',
          marginBottom: '4px',
          textTransform: 'uppercase',
          fontWeight: 600,
          letterSpacing: '0.5px'
        }}>
          {label}
        </div>
        <div style={{ fontSize: '28px', fontWeight: 700, color }}>{value}</div>
      </div>
    </div>
  )
}

function ProposalCard({ proposal, onViewVehicle }) {
  const getStatusBadge = (status) => {
    const badges = {
      'PENDING': { text: '⏱️ En attente', color: '#6c757d' },
      'FAVORITE': { text: '❤️ Coup de cœur', color: '#e91e63' },
      'REJECTED': { text: '❌ Refusé', color: '#dc3545' }
    }
    const badge = badges[status] || badges['PENDING']
    return (
      <span style={{
        background: badge.color,
        color: 'white',
        padding: '4px 10px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: 600
      }}>
        {badge.text}
      </span>
    )
  }

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
      border: proposal.status === 'FAVORITE' ? '2px solid #e91e63' : '2px solid transparent'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '12px'
      }}>
        {getStatusBadge(proposal.status)}
        <span style={{ fontSize: '12px', color: '#6a737d' }}>
          {new Date(proposal.created_at).toLocaleDateString('fr-FR')}
        </span>
      </div>

      <div style={{
        background: '#f8f9fa',
        padding: '12px',
        borderRadius: '8px',
        marginBottom: '12px'
      }}>
        <div style={{ fontWeight: 600, marginBottom: '8px', fontSize: '15px' }}>
          {proposal.vehicle?.title || 'Véhicule'}
        </div>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '6px',
          fontSize: '13px',
          color: '#6a737d'
        }}>
          <div>💰 {proposal.vehicle?.price?.toLocaleString()} €</div>
          <div>📅 {proposal.vehicle?.year}</div>
          <div>🛣️ {proposal.vehicle?.mileage?.toLocaleString()} km</div>
          <div>⛽ {proposal.vehicle?.fuel_type}</div>
        </div>
      </div>

      {proposal.message && (
        <div style={{
          background: '#e7f3ff',
          padding: '10px',
          borderRadius: '8px',
          marginBottom: '12px',
          fontSize: '13px',
          lineHeight: 1.5
        }}>
          <strong style={{ display: 'block', marginBottom: '4px', color: '#667eea' }}>
            Votre message :
          </strong>
          {proposal.message}
        </div>
      )}

      {proposal.rejection_reason && (
        <div style={{
          background: '#ffe7e7',
          padding: '10px',
          borderRadius: '8px',
          marginBottom: '12px',
          fontSize: '13px',
          lineHeight: 1.5,
        }}>
          <strong style={{ display: 'block', marginBottom: '4px', color: '#dc3545' }}>
            Raison du refus :
          </strong>
          {proposal.rejection_reason}
        </div>
      )}

      <button
        onClick={() => onViewVehicle(proposal.vehicle_id)}
        style={{
          width: '100%',
          padding: '10px',
          background: 'white',
          border: '2px solid #667eea',
          color: '#667eea',
          borderRadius: '8px',
          fontSize: '13px',
          fontWeight: 600,
          cursor: 'pointer'
        }}
      >
        👁️ Voir le véhicule
      </button>
    </div>
  )
}

function SearchResultsModal({ results, onClose, onPropose, alreadyProposedIds }) {
  return (
    <div 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.7)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '20px'
      }}
      onClick={onClose}
    >
      <div 
        style={{
          background: 'white',
          borderRadius: '16px',
          padding: '28px',
          maxWidth: '1000px',
          width: '100%',
          maxHeight: '80vh',
          overflow: 'auto',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '24px'
        }}>
          <h2 style={{ margin: 0, fontSize: '22px', fontWeight: 700 }}>
            🔍 Résultats de recherche ({results.length})
          </h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '28px',
              cursor: 'pointer',
              color: '#6a737d'
            }}
          >
            ✕
          </button>
        </div>

        {results.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#6a737d' }}>
            <p>Aucun véhicule trouvé avec ces critères</p>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '16px'
          }}>
            {results.map(result => {
              const vehicle = result.source
              const alreadyProposed = alreadyProposedIds.includes(result.id)
              
              return (
                <div
                  key={result.id}
                  style={{
                    background: alreadyProposed ? '#f0f0f0' : 'white',
                    border: alreadyProposed ? '2px solid #ddd' : '2px solid #e1e4e8',
                    borderRadius: '12px',
                    padding: '16px',
                    opacity: alreadyProposed ? 0.6 : 1
                  }}
                >
                  <div style={{
                    fontWeight: 600,
                    marginBottom: '8px',
                    fontSize: '14px',
                    color: alreadyProposed ? '#6a737d' : '#24292e'
                  }}>
                    {vehicle?.title || 'Sans titre'}
                  </div>
                  
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '6px',
                    fontSize: '12px',
                    color: '#6a737d',
                    marginBottom: '12px'
                  }}>
                    {vehicle?.price && <div>💰 {vehicle.price.toLocaleString()} €</div>}
                    {vehicle?.year && <div>📅 {vehicle.year}</div>}
                    {vehicle?.mileage && <div>🛣️ {vehicle.mileage.toLocaleString()} km</div>}
                    {vehicle?.fuel_type && <div>⛽ {vehicle.fuel_type}</div>}
                  </div>

                  <button
                    onClick={() => onPropose(result.id)}
                    disabled={alreadyProposed}
                    style={{
                      width: '100%',
                      padding: '8px',
                      background: alreadyProposed ? '#ddd' : '#667eea',
                      color: alreadyProposed ? '#999' : 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '13px',
                      fontWeight: 600,
                      cursor: alreadyProposed ? 'not-allowed' : 'pointer'
                    }}
                  >
                    {alreadyProposed ? '✅ Déjà proposé' : '➕ Proposer'}
                  </button>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

function ProposeVehicleModal({ vehicleId, requestCriteria, onClose, onConfirm }) {
  const [message, setMessage] = useState('')
  const [selectedTemplate, setSelectedTemplate] = useState('')

  const templates = [
    {
      id: 'perfect',
      label: '🎯 Correspond parfaitement',
      text: `Ce véhicule correspond parfaitement à vos critères : ${requestCriteria.budget_max ? `budget respecté (${requestCriteria.budget_max}€)` : 'excellent rapport qualité-prix'}, ${requestCriteria.preferred_fuel_type || 'motorisation adaptée'}, et ${requestCriteria.max_mileage ? `faible kilométrage (${requestCriteria.max_mileage} km max)` : 'bon état général'}. Je vous le recommande vivement !`
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

  function useTemplate(template) {
    setMessage(template.text)
    setSelectedTemplate(template.id)
  }

  return (
    <div 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.7)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1001,
        padding: '20px'
      }}
      onClick={onClose}
    >
      <div 
        style={{
          background: 'white',
          borderRadius: '16px',
          padding: '28px',
          maxWidth: '600px',
          width: '100%',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ margin: '0 0 20px 0', fontSize: '22px', fontWeight: 700 }}>
          ➕ Proposer ce véhicule
        </h2>

        <p style={{ color: '#6a737d', fontSize: '14px', marginBottom: '20px' }}>
          Ajoutez un message personnalisé pour expliquer pourquoi ce véhicule correspond aux besoins du client.
        </p>

        {/* Templates */}
        <div style={{ marginBottom: '20px' }}>
          <div style={{
            fontSize: '13px',
            fontWeight: 600,
            marginBottom: '10px',
            color: '#24292e'
          }}>
            💬 Messages rapides :
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {templates.map(template => (
              <button
                key={template.id}
                onClick={() => useTemplate(template)}
                style={{
                  padding: '8px 14px',
                  background: selectedTemplate === template.id ? '#667eea' : '#f0f0f0',
                  color: selectedTemplate === template.id ? 'white' : '#24292e',
                  border: 'none',
                  borderRadius: '20px',
                  fontSize: '12px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                {template.label}
              </button>
            ))}
          </div>
        </div>

        {/* Message personnalisé */}
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Écrivez votre message personnalisé..."
          style={{
            width: '100%',
            padding: '12px',
            border: '2px solid #e1e4e8',
            borderRadius: '8px',
            fontSize: '14px',
            fontFamily: 'inherit',
            minHeight: '120px',
            resize: 'vertical',
            marginBottom: '20px'
          }}
        />

        {/* Actions */}
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={onClose}
            style={{
              flex: 1,
              padding: '12px',
              background: 'white',
              border: '2px solid #e1e4e8',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Annuler
          </button>
          <button
            onClick={() => onConfirm(message)}
            disabled={!message.trim()}
            style={{
              flex: 1,
              padding: '12px',
              background: message.trim() ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#ccc',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: message.trim() ? 'pointer' : 'not-allowed'
            }}
          >
            ✅ Proposer ce véhicule
          </button>
        </div>
      </div>
    </div>
  )
}