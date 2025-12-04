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

export default function ExpertRequestDetailPage() {
  const { requestId } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()

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
    return <div style={{ padding: 'var(--space-10)', textAlign: 'center' }}>Chargement...</div>
  }

  async function handleSearchVehicles() {
    // Rediriger vers la page de recherche dédiée avec les critères pré-appliqués
    const params = new URLSearchParams()

    if (request.budget_max) params.append('budget_max', request.budget_max)
    if (request.preferred_fuel_type) params.append('fuel_type', request.preferred_fuel_type)
    if (request.preferred_transmission) params.append('transmission', request.preferred_transmission)
    if (request.max_mileage) params.append('max_mileage', request.max_mileage)
    if (request.min_year) params.append('min_year', request.min_year)

    navigate(`/expert/requests/${requestId}/search?${params.toString()}`)
  }

  async function handleProposeVehicle(vehicleId, message) {
    try {
      await proposeVehicle(requestId, vehicleId, message)
      mutateProposals()
      setShowProposeModal(false)
      setShowSearchModal(false)
      alert(' Véhicule proposé avec succès !')
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
      alert(' Demande terminée')
      navigate('/expert')
    } catch (error) {
      console.error('Erreur:', error)
      alert('❌ Erreur')
    }
  }

  const stats = {
    proposed: proposals?.length || 0,
    favorites: proposals?.filter(p => p.status === 'SUPER_LIKED' || p.status === 'LIKED').length || 0,
    rejected: proposals?.filter(p => p.status === 'REJECTED').length || 0,
    pending: proposals?.filter(p => p.status === 'PENDING').length || 0
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: 'var(--space-5)' }}>
      {/* Header */}
      <div style={{ marginBottom: '30px' }}>
        <button
          onClick={() => navigate('/expert')}
          style={{
            background: 'var(--white)',
            border: '1px solid #EEEEEE',
            padding: '8px 16px',
                        cursor: 'pointer',
            marginBottom: 'var(--space-4)',
            color: 'var(--text-primary)',
            fontSize: '14px',
            fontWeight: 500,
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'var(--text-primary)';
            e.currentTarget.style.background = 'var(--gray-50)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-light)';
            e.currentTarget.style.background = 'var(--white)';
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
        gap: 'var(--space-4)',
        marginBottom: '30px'
      }}>
        <StatCard icon="📋" label="Propositions" value={stats.proposed} color="var(--text-primary)" />
        <StatCard icon="" label="Coup de cœur" value={stats.favorites} color="var(--red-accent)" />
        <StatCard icon="" label="En attente" value={stats.pending} color="var(--text-secondary)" />
        <StatCard icon="❌" label="Refusés" value={stats.rejected} color="var(--text-muted)" />
      </div>

      {/* Actions principales */}
      <div style={{
        display: 'flex',
        gap: 'var(--space-3)',
        marginBottom: '30px',
        flexWrap: 'wrap'
      }}>
        <button
          onClick={handleSearchVehicles}
          style={{
            flex: '1',
            minWidth: '200px',
            padding: '14px 24px',
            background: 'var(--red-accent)',
            color: 'var(--white)',
            border: 'none',
                        fontSize: '15px',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'background 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = 'var(--red-accent)'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'var(--red-accent)'}
        >
          Rechercher des véhicules
        </button>

        <button
          onClick={handleComplete}
          disabled={request.status === 'TERMINEE'}
          style={{
            padding: '14px 24px',
            background: request.status === 'TERMINEE' ? '#CCCCCC' : 'var(--text-primary)',
            color: 'var(--white)',
            border: 'none',
                        fontSize: '15px',
            fontWeight: 600,
            cursor: request.status === 'TERMINEE' ? 'not-allowed' : 'pointer',
            transition: 'background 0.2s'
          }}
          onMouseEnter={(e) => {
            if (request.status !== 'TERMINEE') {
              e.currentTarget.style.background = '#000000';
            }
          }}
          onMouseLeave={(e) => {
            if (request.status !== 'TERMINEE') {
              e.currentTarget.style.background = 'var(--text-primary)';
            }
          }}
        >
          Terminer la demande
        </button>
      </div>

      {/* Propositions existantes */}
      <div>
        <h2 style={{ fontSize: 'var(--space-5)', fontWeight: 600, marginBottom: 'var(--space-5)' }}>
          Véhicules proposés ({proposals?.length || 0})
        </h2>

        {!proposals || proposals.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            background: 'var(--white)',
                        color: '#6a737d'
          }}>
            <div style={{ fontSize: 'var(--space-12)', marginBottom: 'var(--space-4)' }}></div>
            <p>Aucun véhicule proposé pour le moment</p>
            <p>Utilisez le bouton "Rechercher" ci-dessus</p>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
            gap: 'var(--space-5)'
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
    </div>
  )
}

function RequestCard({ request }) {
  const getStatusBadge = (status) => {
    const badges = {
      'PENDING': { text: 'En attente', color: 'var(--text-secondary)' },
      'IN_PROGRESS': { text: 'En cours', color: 'var(--red-accent)' },
      'COMPLETED': { text: 'Terminée', color: 'var(--text-primary)' },
      'CANCELLED': { text: 'Annulée', color: 'var(--text-muted)' }
    }
    const badge = badges[status] || badges['IN_PROGRESS']
    return (
      <span style={{
        background: badge.color,
        color: 'var(--white)',
        padding: '4px 10px',
                fontSize: '11px',
        fontWeight: 600,
        letterSpacing: '0.5px',
        textTransform: 'uppercase'
      }}>
        {badge.text}
      </span>
    )
  }

  return (
    <div style={{
      background: 'var(--white)',
      padding: 'var(--space-6)',
            boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
      border: '1px solid #EEEEEE'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 'var(--space-5)'
      }}>
        <div>
          <h1 style={{ margin: '0 0 8px 0', fontSize: 'var(--space-6)', fontWeight: 700 }}>
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
        padding: 'var(--space-4)',
                marginBottom: 'var(--space-5)'
      }}>
        <strong style={{ display: 'block', marginBottom: 'var(--space-2)', color: '#24292e' }}>
           Description :
        </strong>
        <p style={{ margin: 0, lineHeight: 1.6, color: '#586069' }}>
          {request.description}
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: 'var(--space-4)'
      }}>
        {request.budget_max && (
          <CriteriaItem
            label="Budget max"
            value={`${request.budget_max.toLocaleString()} €`}
            icon=""
            color="#28a745"
          />
        )}
        {request.preferred_fuel_type && (
          <CriteriaItem
            label="Carburant"
            value={request.preferred_fuel_type}
            icon=""
          />
        )}
        {request.preferred_transmission && (
          <CriteriaItem
            label="Transmission"
            value={request.preferred_transmission}
            icon=""
          />
        )}
        {request.max_mileage && (
          <CriteriaItem
            label="Km max"
            value={`${request.max_mileage.toLocaleString()} km`}
            icon=""
          />
        )}
        {request.min_year && (
          <CriteriaItem
            label="Année min"
            value={request.min_year}
            icon=""
          />
        )}
      </div>
    </div>
  )
}

function CriteriaItem({ label, value, icon, color = '#24292e' }) {
  return (
    <div>
      <div style={{ fontSize: 'var(--space-3)', color: '#6a737d', marginBottom: 'var(--space-1)' }}>
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
      background: 'var(--white)',
      padding: 'var(--space-5)',
            boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
      border: '1px solid #EEEEEE',
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-4)'
    }}>
      <div style={{ fontSize: 'var(--space-8)', lineHeight: 1 }}>{icon}</div>
      <div>
        <div style={{
          fontSize: 'var(--space-3)',
          color: 'var(--text-secondary)',
          marginBottom: 'var(--space-1)',
          textTransform: 'uppercase',
          fontWeight: 600,
          letterSpacing: '0.5px'
        }}>
          {label}
        </div>
        <div style={{ fontSize: 'var(--space-6)', fontWeight: 700, color }}>{value}</div>
      </div>
    </div>
  )
}

function ProposalCard({ proposal, onViewVehicle }) {
  const getStatusBadge = (status) => {
    const badges = {
      'PENDING': { text: 'En attente', color: 'var(--text-secondary)' },
      'LIKED': { text: 'Aimé', color: 'var(--text-primary)' },
      'SUPER_LIKED': { text: 'Coup de cœur', color: 'var(--red-accent)' },
      'REJECTED': { text: 'Refusé', color: 'var(--text-muted)' }
    }
    const badge = badges[status] || badges['PENDING']
    return (
      <span style={{
        background: badge.color,
        color: 'var(--white)',
        padding: '4px 10px',
                fontSize: '11px',
        fontWeight: 600,
        letterSpacing: '0.5px',
        textTransform: 'uppercase'
      }}>
        {badge.text}
      </span>
    )
  }

  return (
    <div style={{
      background: 'var(--white)',
            padding: 'var(--space-5)',
      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
      border: proposal.status === 'SUPER_LIKED' ? '2px solid #DC2626' : '1px solid #EEEEEE'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 'var(--space-3)'
      }}>
        {getStatusBadge(proposal.status)}
        <span style={{ fontSize: 'var(--space-3)', color: '#6a737d' }}>
          {new Date(proposal.created_at).toLocaleDateString('fr-FR')}
        </span>
      </div>

      <div style={{
        background: '#f8f9fa',
        padding: 'var(--space-3)',
                marginBottom: 'var(--space-3)'
      }}>
        <div style={{ fontWeight: 600, marginBottom: 'var(--space-2)', fontSize: '15px' }}>
          {proposal.vehicle?.title || 'Véhicule'}
        </div>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '6px',
          fontSize: '13px',
          color: '#6a737d'
        }}>
          <div> {proposal.vehicle?.price?.toLocaleString()} €</div>
          <div> {proposal.vehicle?.year}</div>
          <div> {proposal.vehicle?.mileage?.toLocaleString()} km</div>
          <div> {proposal.vehicle?.fuel_type}</div>
        </div>
      </div>

      {proposal.message && (
        <div style={{
          background: 'var(--gray-50)',
          padding: '10px',
                    marginBottom: 'var(--space-3)',
          fontSize: '13px',
          lineHeight: 1.5,
          border: '1px solid #EEEEEE'
        }}>
          <strong style={{ display: 'block', marginBottom: 'var(--space-1)', color: 'var(--text-primary)' }}>
            Votre message :
          </strong>
          <div style={{ color: 'var(--text-secondary)' }}>{proposal.message}</div>
        </div>
      )}

      {proposal.rejection_reason && (
        <div style={{
          background: 'var(--gray-50)',
          padding: '10px',
                    marginBottom: 'var(--space-3)',
          fontSize: '13px',
          lineHeight: 1.5,
          border: '1px solid #DC2626'
        }}>
          <strong style={{ display: 'block', marginBottom: 'var(--space-1)', color: 'var(--red-accent)' }}>
            Raison du refus :
          </strong>
          <div style={{ color: 'var(--text-secondary)' }}>{proposal.rejection_reason}</div>
        </div>
      )}

      <button
        onClick={() => onViewVehicle(proposal.vehicle_id)}
        style={{
          width: '100%',
          padding: '10px',
          background: 'var(--white)',
          border: '1px solid #EEEEEE',
          color: 'var(--text-primary)',
                    fontSize: '13px',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'all 0.2s'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = 'var(--text-primary)';
          e.currentTarget.style.background = 'var(--gray-50)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = 'var(--border-light)';
          e.currentTarget.style.background = 'var(--white)';
        }}
      >
        Voir le véhicule
      </button>
    </div>
  )
}
