// frontend/src/Pages/ExpertDashboard.jsx
import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import useSWR from 'swr'
import {
  getAvailableRequests,
  acceptRequest,
  proposeVehicle,
  completeRequest,
  getExpertStats
} from '../services/assisted'
import { apiPost } from '../services/api'

export default function ExpertDashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('available')
  const [selectedRequest, setSelectedRequest] = useState(null)
  const [showProposeModal, setShowProposeModal] = useState(false)

  // Charger les données
  const { data: availableRequests, mutate: mutateAvailable } = useSWR(
    ['/assisted/available', 'EN_ATTENTE'],
    () => getAvailableRequests('EN_ATTENTE')
  )

  const { data: myAssignments, mutate: mutateAssignments } = useSWR(
    ['/assisted/assignments', 'EN_COURS'],
    () => getAvailableRequests('EN_COURS')
  )

  const { data: stats } = useSWR('/assisted/expert/stats', getExpertStats)

  // Vérifier accès expert
  if (!user || user.role !== 'EXPERT') {
    return (
      <div className="access-denied">
        <h2>🔒 Accès réservé aux experts</h2>
        <p>Cette page est uniquement accessible aux comptes experts.</p>
        <button onClick={() => navigate('/')}>Retour à l'accueil</button>
      </div>
    )
  }

  async function handleAcceptRequest(requestId) {
    try {
      await acceptRequest(requestId)
      mutateAvailable()
      mutateAssignments()
      alert('✅ Demande acceptée ! Vous pouvez maintenant proposer des véhicules.')
    } catch (error) {
      console.error('Erreur:', error)
      alert('❌ Erreur lors de l\'acceptation')
    }
  }

  async function handleCompleteRequest(requestId) {
    if (!confirm('Marquer cette demande comme terminée ?')) return

    try {
      await completeRequest(requestId)
      mutateAssignments()
      alert('✅ Demande marquée comme terminée')
    } catch (error) {
      console.error('Erreur:', error)
      alert('❌ Erreur')
    }
  }

  return (
    <div className="expert-dashboard">
      <div className="dashboard-header">
        <div>
          <h1>⭐ Dashboard Expert</h1>
          <p className="subtitle">Aidez les clients à trouver leur véhicule idéal</p>
        </div>
      </div>

      {/* Statistiques */}
      {stats && (
        <div className="kpi-grid">
          <KPICard
            icon="📋"
            label="Demandes traitées"
            value={stats.total_requests}
            color="blue"
          />
          <KPICard
            icon="⏳"
            label="En cours"
            value={stats.pending_requests}
            color="orange"
          />
          <KPICard
            icon="✅"
            label="Terminées"
            value={stats.completed_requests}
            color="green"
          />
          <KPICard
            icon="💚"
            label="Taux d'acceptation"
            value={`${stats.acceptance_rate}%`}
            subtext={`${stats.accepted_proposals}/${stats.total_proposals} véhicules`}
            color="purple"
          />
        </div>
      )}

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'available' ? 'active' : ''}`}
          onClick={() => setActiveTab('available')}
        >
          🆕 Disponibles {availableRequests && `(${availableRequests.length})`}
        </button>
        <button
          className={`tab ${activeTab === 'assignments' ? 'active' : ''}`}
          onClick={() => setActiveTab('assignments')}
        >
          📌 Mes Missions {myAssignments && `(${myAssignments.length})`}
        </button>
      </div>

      {/* Contenu */}
      <div className="tab-content">
        {activeTab === 'available' && (
          <AvailableRequestsTab
            requests={availableRequests}
            onAccept={handleAcceptRequest}
          />
        )}

        {activeTab === 'assignments' && (
          <AssignmentsTab
            assignments={myAssignments}
            onComplete={handleCompleteRequest}
            onPropose={(request) => {
              setSelectedRequest(request)
              setShowProposeModal(true)
            }}
          />
        )}
      </div>

      {/* Modal Proposition */}
      {showProposeModal && selectedRequest && (
        <ProposeVehicleModal
          request={selectedRequest}
          onClose={() => {
            setShowProposeModal(false)
            setSelectedRequest(null)
          }}
          onSuccess={() => {
            setShowProposeModal(false)
            setSelectedRequest(null)
            mutateAssignments()
          }}
        />
      )}
    </div>
  )
}

function KPICard({ icon, label, value, subtext, color }) {
  return (
    <div className={`kpi-card ${color}`}>
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-content">
        <div className="kpi-label">{label}</div>
        <div className="kpi-value">{value}</div>
        {subtext && <div className="kpi-subtext">{subtext}</div>}
      </div>
    </div>
  )
}

function AvailableRequestsTab({ requests, onAccept }) {
  if (!requests) {
    return <div className="loading">Chargement...</div>
  }

  if (requests.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📭</div>
        <h3>Aucune demande disponible</h3>
        <p>Revenez plus tard pour voir de nouvelles demandes</p>
      </div>
    )
  }

  return (
    <div className="requests-grid">
      {requests.map(request => (
        <RequestCard
          key={request.id}
          request={request}
          onAccept={() => onAccept(request.id)}
          showAcceptButton
        />
      ))}
    </div>
  )
}

function AssignmentsTab({ assignments, onComplete, onPropose }) {
  if (!assignments) {
    return <div className="loading">Chargement...</div>
  }

  if ( assignments.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">🎉</div>
        <h3>Pas de missions en cours</h3>
        <p>Acceptez des demandes pour commencer à aider des clients</p>
      </div>
    )
  }
    return (
    <div className="requests-grid">
        {assignments.map(assignment => (
        <RequestCard
            key={assignment.id}
            request={assignment}
            onComplete={() => onComplete(assignment.id)}
            onPropose={() => onPropose(assignment)}
            showProposeButton
        />
        ))}
    </div>
  )
}