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
    try {
      await updateProposalStatus(proposalId, 'LIKED', null)
      await loadData()
      alert(' Véhicule marqué comme coup de cœur !')
    } catch (error) {
      console.error('Error marking favorite:', error)
      alert('❌ Erreur lors de la mise en favori : ' + (error.response?.data?.detail || error.message))
    }
  }

  async function handleReject(proposalId) {
    if (!rejectReason.trim()) {
      alert('Veuillez indiquer une raison')
      return
    }
    try {
      await updateProposalStatus(proposalId, 'REJECTED', rejectReason)
      setShowRejectModal(null)
      setRejectReason('')
      await loadData()
      alert(' Véhicule refusé avec succès')
    } catch (error) {
      console.error('Error rejecting proposal:', error)
      alert('❌ Erreur lors du refus : ' + (error.response?.data?.detail || error.message))
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      'EN_ATTENTE': { text: ' En attente', color: '#ffc107' },
      'EN_COURS': { text: ' En cours', color: '#17a2b8' },
      'TERMINEE': { text: ' Terminée', color: '#28a745' },
      'ANNULEE': { text: '❌ Annulée', color: '#dc3545' }
    }
    const badge = badges[status] || badges['EN_ATTENTE']
    return <span style={{
      background: badge.color,
      color: 'var(--white)',
      padding: '4px 12px',
            fontSize: '13px',
      fontWeight: 600
    }}>{badge.text}</span>
  }

  const getProposalStatusBadge = (status) => {
    const badges = {
      'PENDING': { text: ' En attente', color: '#6c757d' },
      'LIKED': { text: ' Coup de cœur', color: '#e91e63' },
      'SUPER_LIKED': { text: '💖 Coup de foudre', color: '#e91e63' },
      'REJECTED': { text: '❌ Refusé', color: '#dc3545' }
    }
    const badge = badges[status] || badges['PENDING']
    return <span style={{
      background: badge.color,
      color: 'var(--white)',
      padding: '4px 10px',
            fontSize: 'var(--space-3)',
      fontWeight: 600
    }}>{badge.text}</span>
  }

  if (loading) {
    return <div style={{padding: 'var(--space-10)', textAlign: 'center'}}>Chargement...</div>
  }

  if (!request) {
    return <div style={{padding: 'var(--space-10)', textAlign: 'center'}}>Demande non trouvée</div>
  }

  const favorites = proposals.filter(p => p.status === 'LIKED' || p.status === 'SUPER_LIKED')
  const rejected = proposals.filter(p => p.status === 'REJECTED')
  const pending = proposals.filter(p => p.status === 'PENDING')

  return (
    <div style={{maxWidth: '1200px', margin: '0 auto', padding: 'var(--space-5)'}}>
      {/* Header */}
      <div style={{marginBottom: '30px'}}>
        <button
          onClick={() => navigate('/assisted')}
          style={{
            background: 'none',
            border: '1px solid #ddd',
            padding: '8px 16px',
                        cursor: 'pointer',
            marginBottom: 'var(--space-4)'
          }}
        >
          ← Retour à mes demandes
        </button>
        
        <div style={{
          background: 'var(--white)',
          padding: 'var(--space-6)',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
        }}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-4)'}}>
            <div>
              <h1 style={{margin: '0 0 12px 0', fontSize: 'var(--space-6)'}}>
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
            padding: 'var(--space-4)',
                        marginBottom: 'var(--space-4)'
          }}>
            <strong style={{display: 'block', marginBottom: 'var(--space-2)'}}>Description :</strong>
            <p style={{margin: 0, lineHeight: 1.6}}>{request.description}</p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 'var(--space-3)'
          }}>
            {request.budget_max && (
              <div>
                <div style={{fontSize: 'var(--space-3)', color: '#6a737d', marginBottom: 'var(--space-1)'}}>Budget max</div>
                <div style={{fontSize: '18px', fontWeight: 600, color: '#28a745'}}>
                  {request.budget_max.toLocaleString()} €
                </div>
              </div>
            )}
            {request.preferred_fuel_type && (
              <div>
                <div style={{fontSize: 'var(--space-3)', color: '#6a737d', marginBottom: 'var(--space-1)'}}>Carburant</div>
                <div style={{fontSize: 'var(--space-4)', fontWeight: 500}}>
                  {request.preferred_fuel_type}
                </div>
              </div>
            )}
            {request.max_mileage && (
              <div>
                <div style={{fontSize: 'var(--space-3)', color: '#6a737d', marginBottom: 'var(--space-1)'}}>Kilométrage max</div>
                <div style={{fontSize: 'var(--space-4)', fontWeight: 500}}>
                  {request.max_mileage.toLocaleString()} km
                </div>
              </div>
            )}
          </div>

          {request.expert && (
            <div style={{
              marginTop: 'var(--space-4)',
              padding: 'var(--space-3)',
              background: '#e7f3ff',
                            display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-3)'
            }}>
              <div style={{
                width: 'var(--space-10)',
                height: 'var(--space-10)',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--white)',
                fontSize: '18px',
                fontWeight: 600
              }}>
                {request.expert.full_name[0]}
              </div>
              <div>
                <div style={{fontWeight: 600}}> Expert assigné</div>
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
        gap: 'var(--space-4)',
        marginBottom: '30px'
      }}>
        <StatCard 
          icon="📋" 
          label="Propositions" 
          value={proposals.length}
          color="#667eea"
        />
        <StatCard 
          icon="" 
          label="Coups de cœur" 
          value={favorites.length}
          color="#e91e63"
        />
        <StatCard 
          icon="" 
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
      background: 'var(--white)',
      padding: 'var(--space-5)',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-4)'
    }}>
      <div style={{
        fontSize: 'var(--space-10)',
        lineHeight: 1
      }}>{icon}</div>
      <div>
        <div style={{
          fontSize: 'var(--space-3)',
          color: '#6a737d',
          marginBottom: 'var(--space-1)',
          textTransform: 'uppercase',
          fontWeight: 600,
          letterSpacing: '0.5px'
        }}>{label}</div>
        <div style={{
          fontSize: 'var(--space-7)',
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
        gap: 'var(--space-2)',
        marginBottom: 'var(--space-5)',
        background: 'var(--white)',
        padding: 'var(--space-2)',
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
          label={` En attente (${pending.length})`}
        />
        <TabButton 
          active={activeTab === 'favorites'} 
          onClick={() => setActiveTab('favorites')}
          label={` Coups de cœur (${favorites.length})`}
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
        gap: 'var(--space-5)'
      }}>
        {getFilteredProposals().length === 0 ? (
          <div style={{
            gridColumn: '1 / -1',
            textAlign: 'center',
            padding: '60px 20px',
            color: '#6a737d'
          }}>
            <div style={{fontSize: 'var(--space-12)', marginBottom: 'var(--space-4)'}}></div>
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
        color: active ? 'var(--white)' : '#6a737d',
        border: 'none',
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
      'PENDING': { text: ' En attente', color: '#6c757d' },
      'FAVORITE': { text: ' Coup de cœur', color: '#e91e63' },
      'REJECTED': { text: '❌ Refusé', color: '#dc3545' }
    }
    const badge = badges[status] || badges['PENDING']
    return (
      <span style={{
        background: badge.color,
        color: 'var(--white)',
        padding: '4px 10px',
                fontSize: '11px',
        fontWeight: 600
      }}>
        {badge.text}
      </span>
    )
  }

  return (
    <div style={{
      background: 'var(--white)',
            padding: 'var(--space-5)',
      boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
      border: status === 'FAVORITE' ? '2px solid #e91e63' : '2px solid transparent',
      transition: 'all 0.3s'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 'var(--space-4)'
      }}>
        {getStatusBadge(status)}
        <span style={{fontSize: 'var(--space-3)', color: '#6a737d'}}>
          {new Date(created_at).toLocaleDateString('fr-FR')}
        </span>
      </div>

      {/* Vehicle Info */}
      <div style={{
        background: '#f8f9fa',
        padding: 'var(--space-4)',
                marginBottom: 'var(--space-3)'
      }}>
        <h3 style={{
          margin: '0 0 12px 0',
          fontSize: 'var(--space-4)',
          fontWeight: 600
        }}>
          {vehicle.title}
        </h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: 'var(--space-2)',
          fontSize: '13px',
          color: '#6a737d'
        }}>
          <div> {vehicle.price.toLocaleString()} €</div>
          <div> {vehicle.year}</div>
          <div> {vehicle.mileage.toLocaleString()} km</div>
          <div> {vehicle.fuel_type}</div>
        </div>
      </div>

      {/* Expert Message */}
      {message && (
        <div style={{
          background: '#e7f3ff',
          padding: 'var(--space-3)',
                    marginBottom: 'var(--space-4)',
          fontSize: '13px',
          lineHeight: 1.5,
          color: '#24292e'
        }}>
          <strong style={{display: 'block', marginBottom: 'var(--space-1)', color: '#667eea'}}>
             Message de l'expert :
          </strong>
          {message}
        </div>
      )}

      {/* Actions */}
      <div style={{display: 'flex', gap: 'var(--space-2)'}}>
        <button
          onClick={() => onViewVehicle(proposal.vehicle_id)}
          style={{
            flex: 1,
            padding: '10px',
            background: 'var(--white)',
            border: '2px solid #667eea',
            color: '#667eea',
                        fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.target.style.background = '#667eea'
            e.target.style.color = 'var(--white)'
          }}
          onMouseLeave={(e) => {
            e.target.style.background = 'var(--white)'
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
                color: 'var(--white)',
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
              
            </button>
            <button
              onClick={onReject}
              style={{
                padding: '10px 16px',
                background: '#dc3545',
                border: 'none',
                color: 'var(--white)',
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
        padding: 'var(--space-5)'
      }}
      onClick={onClose}
    >
      <div 
        style={{
          background: 'var(--white)',
                    padding: 'var(--space-7)',
          maxWidth: '500px',
          width: '100%',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{margin: '0 0 20px 0', fontSize: 'var(--space-5)'}}>
          ❌ Refuser cette proposition
        </h2>
        
        <p style={{color: '#6a737d', fontSize: '14px', marginBottom: 'var(--space-4)'}}>
          Indiquez pourquoi ce véhicule ne vous convient pas. Cela aidera l'expert à mieux comprendre vos besoins.
        </p>

        {/* Predefined reasons */}
        <div style={{marginBottom: 'var(--space-4)'}}>
          <div style={{
            fontSize: '13px',
            fontWeight: 600,
            marginBottom: 'var(--space-2)',
            color: '#24292e'
          }}>
            Raisons courantes :
          </div>
          <div style={{display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)'}}>
            {predefinedReasons.map(r => (
              <button
                key={r}
                onClick={() => onReasonChange(r)}
                style={{
                  padding: '8px 14px',
                  background: reason === r ? '#667eea' : '#f0f0f0',
                  color: reason === r ? 'var(--white)' : '#24292e',
                  border: 'none',
                                    fontSize: 'var(--space-3)',
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
            padding: 'var(--space-3)',
            border: '2px solid #e1e4e8',
                        fontSize: '14px',
            fontFamily: 'inherit',
            minHeight: 'var(--space-20)',
            resize: 'vertical',
            marginBottom: 'var(--space-5)'
          }}
        />

        {/* Actions */}
        <div style={{display: 'flex', gap: 'var(--space-3)'}}>
          <button
            onClick={onClose}
            style={{
              flex: 1,
              padding: 'var(--space-3)',
              background: 'var(--white)',
              border: '2px solid #e1e4e8',
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
              padding: 'var(--space-3)',
              background: reason.trim() ? '#dc3545' : '#ccc',
              border: 'none',
              color: 'var(--white)',
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