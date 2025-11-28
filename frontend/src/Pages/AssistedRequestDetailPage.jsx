import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  getRequestDetail,
  getMyProposals,
  updateProposalStatus
} from '../services/assisted'

export default function AssistedRequestDetailPage() {
  const { requestId } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  
  const [request, setRequest] = useState(null)
  const [proposals, setProposals] = useState([])
  const [loading, setLoading] = useState(true)
  const [showRejectModal, setShowRejectModal] = useState(null)
  const [rejectReason, setRejectReason] = useState('')

  useEffect(() => {
    loadData()
  }, [requestId])

  async function loadData() {
    try {
      const [reqData, propsData] = await Promise.all([
        getRequestDetail(requestId),
        getMyProposals(requestId)
      ])
      setRequest(reqData)
      setProposals(propsData)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  async function handleMarkFavorite(proposalId) {
    await updateProposalStatus(proposalId, 'FAVORITE', null)
    await loadData()
  }

  async function handleReject(proposalId) {
    if (!rejectReason.trim()) {
      alert('Veuillez indiquer une raison')
      return
    }
    await updateProposalStatus(proposalId, 'REJECTED', rejectReason)
    setShowRejectModal(null)
    setRejectReason('')
    await loadData()
  }

  const getStatusBadge = (status) => {
    const badges = {
      'EN_ATTENTE': { text: '⏳ En attente', color: '#ffc107' },
      'EN_COURS': { text: '🔄 En cours', color: '#17a2b8' },
      'TERMINEE': { text: '✅ Terminée', color: '#28a745' },
      'ANNULEE': { text: '❌ Annulée', color: '#dc3545' }
    }
    const badge = badges[status] || badges['EN_ATTENTE']
    return <span style={{
      background: badge.color,
      color: 'white',
      padding: '4px 12px',
      borderRadius: '16px',
      fontSize: '13px',
      fontWeight: 600
    }}>{badge.text}</span>
  }

  const getProposalStatusBadge = (status) => {
    const badges = {
      'PENDING': { text: '⏱️ En attente', color: '#6c757d' },
      'FAVORITE': { text: '❤️ Coup de cœur', color: '#e91e63' },
      'REJECTED': { text: '❌ Refusé', color: '#dc3545' }
    }
    const badge = badges[status] || badges['PENDING']
    return <span style={{
      background: badge.color,
      color: 'white',
      padding: '4px 10px',
      borderRadius: '12px',
      fontSize: '12px',
      fontWeight: 600
    }}>{badge.text}</span>
  }

  if (loading) {
    return <div style={{padding: '40px', textAlign: 'center'}}>Chargement...</div>
  }

  if (!request) {
    return <div style={{padding: '40px', textAlign: 'center'}}>Demande non trouvée</div>
  }

  const favorites = proposals.filter(p => p.status === 'FAVORITE')
  const rejected = proposals.filter(p => p.status === 'REJECTED')
  const pending = proposals.filter(p => p.status === 'PENDING')

  return (
    <div style={{maxWidth: '1200px', margin: '0 auto', padding: '20px'}}>
      {/* Header */}
      <div style={{marginBottom: '30px'}}>
        <button
          onClick={() => navigate('/assisted')}
          style={{
            background: 'none',
            border: '1px solid #ddd',
            padding: '8px 16px',
            borderRadius: '8px',
            cursor: 'pointer',
            marginBottom: '16px'
          }}
        >
          ← Retour à mes demandes
        </button>
        
        <div style={{
          background: 'white',
          padding: '24px',
          borderRadius: '16px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
        }}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px'}}>
            <div>
              <h1 style={{margin: '0 0 12px 0', fontSize: '24px'}}>
                Ma demande assistée
              </h1>
              <p style={{color: '#6a737d', margin: 0, fontSize: '14px'}}>
                Créée le {new Date(request.created_at).toLocaleDateString('fr-FR')}
              </p>
            </div>
            {getStatusBadge(request.status)}
          </div>

          <div style={{
            background: '#f8f9fa',
            padding: '16px',
            borderRadius: '12px',
            marginBottom: '16px'
          }}>
            <strong style={{display: 'block', marginBottom: '8px'}}>Description :</strong>
            <p style={{margin: 0, lineHeight: 1.6}}>{request.description}</p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '12px'
          }}>
            {request.budget_max && (
              <div>
                <div style={{fontSize: '12px', color: '#6a737d', marginBottom: '4px'}}>Budget max</div>
                <div style={{fontSize: '18px', fontWeight: 600, color: '#28a745'}}>
                  {request.budget_max.toLocaleString()} €
                </div>
              </div>
            )}
            {request.preferred_fuel_type && (
              <div>
                <div style={{fontSize: '12px', color: '#6a737d', marginBottom: '4px'}}>Carburant</div>
                <div style={{fontSize: '16px', fontWeight: 500}}>
                  {request.preferred_fuel_type}
                </div>
              </div>
            )}
            {request.max_mileage && (
              <div>
                <div style={{fontSize: '12px', color: '#6a737d', marginBottom: '4px'}}>Kilométrage max</div>
                <div style={{fontSize: '16px', fontWeight: 500}}>
                  {request.max_mileage.toLocaleString()} km
                </div>
              </div>
            )}
          </div>

          {request.expert && (
            <div style={{
              marginTop: '16px',
              padding: '12px',
              background: '#e7f3ff',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '18px',
                fontWeight: 600
              }}>
                {request.expert.full_name[0]}
              </div>
              <div>
                <div style={{fontWeight: 600}}>⭐ Expert assigné</div>
                <div style={{fontSize: '13px', color: '#6a737d'}}>
                  {request.expert.full_name}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Stats */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '30px'
      }}>
        <StatCard 
          icon="📋" 
          label="Propositions" 
          value={proposals.length}
          color="#667eea"
        />
        <StatCard 
          icon="❤️" 
          label="Coups de cœur" 
          value={favorites.length}
          color="#e91e63"
        />
        <StatCard 
          icon="⏱️" 
          label="En attente" 
          value={pending.length}
          color="#ffc107"
        />
        <StatCard 
          icon="❌" 
          label="Refusés" 
          value={rejected.length}
          color="#dc3545"
        />
      </div>

      {/* Tabs */}
      <TabSection 
        proposals={proposals}
        pending={pending}
        favorites={favorites}
        rejected={rejected}
        onFavorite={handleMarkFavorite}
        onReject={(id) => setShowRejectModal(id)}
        onViewVehicle={(vehicleId) => {
          window.open(`/vehicle/${vehicleId}`, '_blank')
        }}
      />

      {/* Reject Modal */}
      {showRejectModal && (
        <RejectModal
          onClose={() => {
            setShowRejectModal(null)
            setRejectReason('')
          }}
          onConfirm={() => handleReject(showRejectModal)}
          reason={rejectReason}
          onReasonChange={setRejectReason}
        />
      )}
    </div>
  )
}

// Stat Card Component
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
      <div style={{
        fontSize: '40px',
        lineHeight: 1
      }}>{icon}</div>
      <div>
        <div style={{
          fontSize: '12px',
          color: '#6a737d',
          marginBottom: '4px',
          textTransform: 'uppercase',
          fontWeight: 600,
          letterSpacing: '0.5px'
        }}>{label}</div>
        <div style={{
          fontSize: '28px',
          fontWeight: 700,
          color: color
        }}>{value}</div>
      </div>
    </div>
  )
}

// Tab Section Component
function TabSection({ proposals, pending, favorites, rejected, onFavorite, onReject, onViewVehicle }) {
  const [activeTab, setActiveTab] = useState('all')
  
  const getFilteredProposals = () => {
    switch(activeTab) {
      case 'pending': return pending
      case 'favorites': return favorites
      case 'rejected': return rejected
      default: return proposals
    }
  }

  return (
    <div>
      {/* Tabs */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '20px',
        background: 'white',
        padding: '8px',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
      }}>
        <TabButton 
          active={activeTab === 'all'} 
          onClick={() => setActiveTab('all')}
          label={`Toutes (${proposals.length})`}
        />
        <TabButton 
          active={activeTab === 'pending'} 
          onClick={() => setActiveTab('pending')}
          label={`⏱️ En attente (${pending.length})`}
        />
        <TabButton 
          active={activeTab === 'favorites'} 
          onClick={() => setActiveTab('favorites')}
          label={`❤️ Coups de cœur (${favorites.length})`}
        />
        <TabButton 
          active={activeTab === 'rejected'} 
          onClick={() => setActiveTab('rejected')}
          label={`❌ Refusés (${rejected.length})`}
        />
      </div>

      {/* Content */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
        gap: '20px'
      }}>
        {getFilteredProposals().length === 0 ? (
          <div style={{
            gridColumn: '1 / -1',
            textAlign: 'center',
            padding: '60px 20px',
            color: '#6a737d'
          }}>
            <div style={{fontSize: '48px', marginBottom: '16px'}}>📭</div>
            <p>Aucune proposition dans cette catégorie</p>
          </div>
        ) : (
          getFilteredProposals().map(proposal => (
            <ProposalCard
              key={proposal.id}
              proposal={proposal}
              onFavorite={() => onFavorite(proposal.id)}
              onReject={() => onReject(proposal.id)}
              onViewVehicle={onViewVehicle}
            />
          ))
        )}
      </div>
    </div>
  )
}

// Tab Button Component
function TabButton({ active, onClick, label }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '12px 20px',
        background: active 
          ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
          : 'transparent',
        color: active ? 'white' : '#6a737d',
        border: 'none',
        borderRadius: '8px',
        fontSize: '14px',
        fontWeight: active ? 600 : 500,
        cursor: 'pointer',
        transition: 'all 0.2s',
        whiteSpace: 'nowrap'
      }}
      onMouseEnter={(e) => {
        if (!active) e.target.style.background = '#f8f9fa'
      }}
      onMouseLeave={(e) => {
        if (!active) e.target.style.background = 'transparent'
      }}
    >
      {label}
    </button>
  )
}

// Proposal Card Component
function ProposalCard({ proposal, onFavorite, onReject, onViewVehicle }) {
  const { vehicle, message, status, created_at } = proposal
  
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
        fontSize: '11px',
        fontWeight: 600
      }}>
        {badge.text}
      </span>
    )
  }

  return (
    <div style={{
      background: 'white',
      borderRadius: '16px',
      padding: '20px',
      boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
      border: status === 'FAVORITE' ? '2px solid #e91e63' : '2px solid transparent',
      transition: 'all 0.3s'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '16px'
      }}>
        {getStatusBadge(status)}
        <span style={{fontSize: '12px', color: '#6a737d'}}>
          {new Date(created_at).toLocaleDateString('fr-FR')}
        </span>
      </div>

      {/* Vehicle Info */}
      <div style={{
        background: '#f8f9fa',
        padding: '16px',
        borderRadius: '12px',
        marginBottom: '12px'
      }}>
        <h3 style={{
          margin: '0 0 12px 0',
          fontSize: '16px',
          fontWeight: 600
        }}>
          {vehicle.title}
        </h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '8px',
          fontSize: '13px',
          color: '#6a737d'
        }}>
          <div>💰 {vehicle.price.toLocaleString()} €</div>
          <div>📅 {vehicle.year}</div>
          <div>🛣️ {vehicle.mileage.toLocaleString()} km</div>
          <div>⛽ {vehicle.fuel_type}</div>
        </div>
      </div>

      {/* Expert Message */}
      {message && (
        <div style={{
          background: '#e7f3ff',
          padding: '12px',
          borderRadius: '8px',
          marginBottom: '16px',
          fontSize: '13px',
          lineHeight: 1.5,
          color: '#24292e'
        }}>
          <strong style={{display: 'block', marginBottom: '4px', color: '#667eea'}}>
            💬 Message de l'expert :
          </strong>
          {message}
        </div>
      )}

      {/* Actions */}
      <div style={{display: 'flex', gap: '8px'}}>
        <button
          onClick={() => onViewVehicle(proposal.vehicle_id)}
          style={{
            flex: 1,
            padding: '10px',
            background: 'white',
            border: '2px solid #667eea',
            color: '#667eea',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.target.style.background = '#667eea'
            e.target.style.color = 'white'
          }}
          onMouseLeave={(e) => {
            e.target.style.background = 'white'
            e.target.style.color = '#667eea'
          }}
        >
          👁️ Voir détails
        </button>
        
        {status === 'PENDING' && (
          <>
            <button
              onClick={onFavorite}
              style={{
                padding: '10px 16px',
                background: '#e91e63',
                border: 'none',
                color: 'white',
                borderRadius: '8px',
                fontSize: '18px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'scale(1.1)'
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'scale(1)'
              }}
            >
              ❤️
            </button>
            <button
              onClick={onReject}
              style={{
                padding: '10px 16px',
                background: '#dc3545',
                border: 'none',
                color: 'white',
                borderRadius: '8px',
                fontSize: '18px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'scale(1.1)'
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'scale(1)'
              }}
            >
              ❌
            </button>
          </>
        )}
      </div>
    </div>
  )
}

// Reject Modal Component
function RejectModal({ onClose, onConfirm, reason, onReasonChange }) {
  const predefinedReasons = [
    'Prix trop élevé',
    'Trop de kilométrage',
    'Pas le bon modèle',
    'Mauvaise localisation',
    'Année trop ancienne',
    'Ne correspond pas à mes attentes'
  ]

  return (
    <div 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.6)',
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
          maxWidth: '500px',
          width: '100%',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{margin: '0 0 20px 0', fontSize: '20px'}}>
          ❌ Refuser cette proposition
        </h2>
        
        <p style={{color: '#6a737d', fontSize: '14px', marginBottom: '16px'}}>
          Indiquez pourquoi ce véhicule ne vous convient pas. Cela aidera l'expert à mieux comprendre vos besoins.
        </p>

        {/* Predefined reasons */}
        <div style={{marginBottom: '16px'}}>
          <div style={{
            fontSize: '13px',
            fontWeight: 600,
            marginBottom: '8px',
            color: '#24292e'
          }}>
            Raisons courantes :
          </div>
          <div style={{display: 'flex', flexWrap: 'wrap', gap: '8px'}}>
            {predefinedReasons.map(r => (
              <button
                key={r}
                onClick={() => onReasonChange(r)}
                style={{
                  padding: '8px 14px',
                  background: reason === r ? '#667eea' : '#f0f0f0',
                  color: reason === r ? 'white' : '#24292e',
                  border: 'none',
                  borderRadius: '20px',
                  fontSize: '12px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                {r}
              </button>
            ))}
          </div>
        </div>

        {/* Custom reason */}
        <textarea
          value={reason}
          onChange={(e) => onReasonChange(e.target.value)}
          placeholder="Ou écrivez votre propre raison..."
          style={{
            width: '100%',
            padding: '12px',
            border: '2px solid #e1e4e8',
            borderRadius: '8px',
            fontSize: '14px',
            fontFamily: 'inherit',
            minHeight: '80px',
            resize: 'vertical',
            marginBottom: '20px'
          }}
        />

        {/* Actions */}
        <div style={{display: 'flex', gap: '12px'}}>
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
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            Annuler
          </button>
          <button
            onClick={onConfirm}
            disabled={!reason.trim()}
            style={{
              flex: 1,
              padding: '12px',
              background: reason.trim() ? '#dc3545' : '#ccc',
              border: 'none',
              color: 'white',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: reason.trim() ? 'pointer' : 'not-allowed',
              transition: 'all 0.2s'
            }}
          >
            Confirmer le refus
          </button>
        </div>
      </div>
    </div>
  )
}