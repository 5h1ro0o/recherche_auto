// frontend/src/Pages/ExpertDashboard.jsx - VERSION AMÉLIORÉE
import React, { useState, useMemo } from 'react'
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
  
  // États pour les filtres
  const [budgetFilter, setBudgetFilter] = useState('')
  const [sortBy, setSortBy] = useState('recent') // recent, budget, urgent
  const [searchTerm, setSearchTerm] = useState('')

  // Charger les données
  const { data: availableRequests, mutate: mutateAvailable } = useSWR(
    ['/assisted/available', 'PENDING'],
    () => getAvailableRequests('PENDING')
  )

  const { data: myAssignments, mutate: mutateAssignments } = useSWR(
    ['/assisted/assignments', 'IN_PROGRESS'],
    () => getAvailableRequests('IN_PROGRESS')
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

  // Fonction de tri et filtrage avancé
  const filteredAndSortedRequests = useMemo(() => {
    if (!availableRequests) return []
    
    let filtered = [...availableRequests]
    
    // Filtre par budget
    if (budgetFilter) {
      const maxBudget = parseInt(budgetFilter)
      filtered = filtered.filter(r => 
        !r.budget_max || r.budget_max <= maxBudget
      )
    }
    
    // Filtre par recherche texte
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(r =>
        r.description?.toLowerCase().includes(term) ||
        r.preferred_fuel_type?.toLowerCase().includes(term)
      )
    }
    
    // Tri
    switch (sortBy) {
      case 'urgent':
        // Demandes > 48h en premier
        filtered.sort((a, b) => {
          const ageA = Date.now() - new Date(a.created_at).getTime()
          const ageB = Date.now() - new Date(b.created_at).getTime()
          return ageB - ageA
        })
        break
      
      case 'budget':
        // Budget le plus élevé en premier
        filtered.sort((a, b) => (b.budget_max || 0) - (a.budget_max || 0))
        break
      
      case 'relevance':
        // Score de pertinence (basé sur critères remplis)
        filtered.sort((a, b) => {
          const scoreA = calculateRelevanceScore(a)
          const scoreB = calculateRelevanceScore(b)
          return scoreB - scoreA
        })
        break
      
      default: // 'recent'
        filtered.sort((a, b) => 
          new Date(b.created_at) - new Date(a.created_at)
        )
    }
    
    return filtered
  }, [availableRequests, budgetFilter, sortBy, searchTerm])

  // Calcul du score de pertinence
  function calculateRelevanceScore(request) {
    let score = 0
    if (request.budget_max) score += 2
    if (request.preferred_fuel_type) score += 1
    if (request.preferred_transmission) score += 1
    if (request.max_mileage) score += 1
    if (request.min_year) score += 1
    if (request.description?.length > 50) score += 2
    return score
  }

  // Identifier les demandes urgentes (> 48h)
  function isUrgent(createdAt) {
    const age = Date.now() - new Date(createdAt).getTime()
    return age > 48 * 60 * 60 * 1000 // 48 heures
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

  // Export PDF des propositions
  async function handleExportPDF(requestId) {
    try {
      // Appel API pour générer le PDF (à implémenter côté backend)
      const response = await apiPost(`/assisted/requests/${requestId}/export-pdf`, {})
      
      // Télécharger le PDF
      const blob = new Blob([response], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `demande_${requestId}.pdf`
      a.click()
      
      alert('✅ PDF exporté avec succès')
    } catch (error) {
      console.error('Erreur export PDF:', error)
      alert('❌ Erreur lors de l\'export PDF')
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

      {/* Statistiques enrichies */}
      {stats && (
        <div className="kpi-grid">
          <KPICard
            icon="📋"
            label="Demandes traitées"
            value={stats.total_requests}
            trend={stats.total_requests > 0 ? `+${stats.total_requests}` : '0'}
            color="blue"
          />
          <KPICard
            icon="⏳"
            label="En cours"
            value={stats.pending_requests}
            subtext={`${Math.round((stats.pending_requests / (stats.total_requests || 1)) * 100)}% du total`}
            color="orange"
          />
          <KPICard
            icon="✅"
            label="Terminées"
            value={stats.completed_requests}
            subtext={`Taux: ${Math.round((stats.completed_requests / (stats.total_requests || 1)) * 100)}%`}
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
          🆕 Disponibles {availableRequests && `(${filteredAndSortedRequests.length})`}
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
            requests={filteredAndSortedRequests}
            onAccept={handleAcceptRequest}
            budgetFilter={budgetFilter}
            setBudgetFilter={setBudgetFilter}
            sortBy={sortBy}
            setSortBy={setSortBy}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            isUrgent={isUrgent}
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
            onExportPDF={handleExportPDF}
            isUrgent={isUrgent}
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

function KPICard({ icon, label, value, subtext, trend, color }) {
  return (
    <div className={`kpi-card ${color}`}>
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-content">
        <div className="kpi-label">{label}</div>
        <div className="kpi-value">
          {value}
          {trend && <span className="kpi-trend">{trend}</span>}
        </div>
        {subtext && <div className="kpi-subtext">{subtext}</div>}
      </div>
    </div>
  )
}

function AvailableRequestsTab({ 
  requests, 
  onAccept, 
  budgetFilter, 
  setBudgetFilter,
  sortBy,
  setSortBy,
  searchTerm,
  setSearchTerm,
  isUrgent
}) {
  if (!requests) {
    return <div className="loading">Chargement...</div>
  }

  return (
    <div className="available-requests-tab">
      {/* Barre de filtres et tri */}
      <div className="filters-bar">
        <input
          type="text"
          placeholder="🔍 Rechercher dans les descriptions..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        
        <select 
          value={budgetFilter} 
          onChange={(e) => setBudgetFilter(e.target.value)}
          className="budget-filter"
        >
          <option value="">💰 Tous les budgets</option>
          <option value="10000">≤ 10 000 €</option>
          <option value="15000">≤ 15 000 €</option>
          <option value="20000">≤ 20 000 €</option>
          <option value="30000">≤ 30 000 €</option>
          <option value="50000">≤ 50 000 €</option>
        </select>

        <select 
          value={sortBy} 
          onChange={(e) => setSortBy(e.target.value)}
          className="sort-select"
        >
          <option value="recent">📅 Plus récentes</option>
          <option value="urgent">🚨 Plus urgentes (48h)</option>
          <option value="budget">💵 Budget décroissant</option>
          <option value="relevance">🎯 Pertinence (critères)</option>
        </select>
      </div>

      {requests.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h3>Aucune demande ne correspond aux filtres</h3>
          <p>Modifiez vos critères de recherche ou réinitialisez les filtres</p>
          <button 
            onClick={() => {
              setBudgetFilter('')
              setSearchTerm('')
              setSortBy('recent')
            }}
            className="btn-reset"
          >
            🔄 Réinitialiser les filtres
          </button>
        </div>
      ) : (
        <div className="requests-grid">
          {requests.map(request => (
            <RequestCard
              key={request.id}
              request={request}
              onAccept={() => onAccept(request.id)}
              showAcceptButton
              isUrgent={isUrgent(request.created_at)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function AssignmentsTab({ assignments, onComplete, onPropose, onExportPDF, isUrgent }) {
  if (!assignments) {
    return <div className="loading">Chargement...</div>
  }

  if (assignments.length === 0) {
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
          onExportPDF={() => onExportPDF(assignment.id)}
          showProposeButton
          showExportButton
          isUrgent={isUrgent(assignment.created_at)}
        />
      ))}
    </div>
  )
}

function RequestCard({ 
  request, 
  onAccept, 
  onComplete, 
  onPropose,
  onExportPDF,
  showAcceptButton,
  showProposeButton,
  showExportButton,
  isUrgent 
}) {
  const navigate = useNavigate()
  
  // Calcul de l'âge de la demande
  const age = Math.floor((Date.now() - new Date(request.created_at).getTime()) / (1000 * 60 * 60))
  
  return (
    <div className={`request-card ${isUrgent ? 'urgent' : ''}`}>
      <div className="card-header">
        <div className="header-badges">
          <span className={`status-badge status-${request.status.toLowerCase()}`}>
            {request.status}
          </span>
          {isUrgent && (
            <span className="urgent-badge" title="Demande > 48h">
              🚨 URGENT
            </span>
          )}
        </div>
        <span className="date" title={new Date(request.created_at).toLocaleString('fr-FR')}>
          Il y a {age}h
        </span>
      </div>

      <div className="card-body">
        <div className="client-info">
          👤 {request.client?.full_name || request.client?.email}
        </div>
        
        <div className="description">
          {request.description}
        </div>

        <div className="criteria-tags">
          {request.budget_max && (
            <span className="tag budget-tag">
              💰 Max {request.budget_max.toLocaleString()} €
            </span>
          )}
          {request.preferred_fuel_type && (
            <span className="tag">⛽ {request.preferred_fuel_type}</span>
          )}
          {request.preferred_transmission && (
            <span className="tag">⚙️ {request.preferred_transmission}</span>
          )}
          {request.max_mileage && (
            <span className="tag">🛣️ Max {request.max_mileage.toLocaleString()} km</span>
          )}
          {request.min_year && (
            <span className="tag">📅 Depuis {request.min_year}</span>
          )}
        </div>

        {request.ai_parsed_criteria && Object.keys(request.ai_parsed_criteria).length > 0 && (
          <div className="ai-criteria">
            <strong>🤖 Critères IA détectés :</strong>
            <div className="criteria-tags">
              {Object.entries(request.ai_parsed_criteria).slice(0, 3).map(([key, value]) => (
                <span key={key} className="tag ai-tag">
                  {key}: {JSON.stringify(value)}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="card-actions">
        {showAcceptButton && (
          <button onClick={onAccept} className="btn-accept">
            ✅ Accepter
          </button>
        )}
        
        {showProposeButton && (
          <>
            <button onClick={onPropose} className="btn-propose">
              🔍 Proposer véhicule
            </button>
            <button 
              onClick={() => navigate(`/expert/request/${request.id}`)} 
              className="btn-view-detail"
            >
              👁️ Détails
            </button>
          </>
        )}

        {showExportButton && (
          <button onClick={onExportPDF} className="btn-export" title="Exporter en PDF">
            📄 PDF
          </button>
        )}
        
        {onComplete && (
          <button onClick={onComplete} className="btn-complete">
            ✅ Terminer
          </button>
        )}
      </div>
    </div>
  )
}

function ProposeVehicleModal({ request, onClose, onSuccess }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [selectedVehicle, setSelectedVehicle] = useState(null)
  const [message, setMessage] = useState('')

  async function handleSearch() {
    setSearching(true)
    try {
      const filters = {}
      if (request.budget_max) filters.price_max = request.budget_max
      if (request.preferred_fuel_type) filters.fuel_type = request.preferred_fuel_type
      if (request.max_mileage) filters.mileage_max = request.max_mileage
      
      const response = await apiPost('/search', {
        q: searchQuery || null,
        filters,
        size: 20
      })
      
      setSearchResults(response.hits || [])
    } catch (error) {
      console.error('Erreur recherche:', error)
      alert('❌ Erreur lors de la recherche')
    } finally {
      setSearching(false)
    }
  }

  async function handlePropose() {
    if (!selectedVehicle || !message.trim()) {
      alert('Veuillez sélectionner un véhicule et ajouter un message')
      return
    }

    try {
      await proposeVehicle(request.id, selectedVehicle, message)
      alert('✅ Véhicule proposé avec succès')
      onSuccess()
    } catch (error) {
      console.error('Erreur:', error)
      alert('❌ Erreur lors de la proposition')
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content large" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🔍 Rechercher et proposer un véhicule</h2>
          <button onClick={onClose} className="close-modal">✕</button>
        </div>

        <div style={{ padding: '24px' }}>
          {/* Recherche */}
          <div className="search-section">
            <input
              type="text"
              placeholder="Rechercher un véhicule..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              style={{ width: '100%', marginBottom: '12px' }}
            />
            <button 
              onClick={handleSearch} 
              disabled={searching}
              className="btn-primary"
            >
              {searching ? '🔍 Recherche...' : '🔍 Rechercher'}
            </button>
          </div>

          {/* Résultats */}
          {searchResults.length > 0 && (
            <div className="search-results" style={{ marginTop: '20px' }}>
              <h3>Résultats ({searchResults.length})</h3>
              <div className="vehicles-list">
                {searchResults.map(result => (
                  <div
                    key={result.id}
                    className={`vehicle-item ${selectedVehicle === result.id ? 'selected' : ''}`}
                    onClick={() => setSelectedVehicle(result.id)}
                  >
                    <strong>{result.source?.title}</strong>
                    <div>{result.source?.price} € • {result.source?.year}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Message */}
          {selectedVehicle && (
            <div style={{ marginTop: '20px' }}>
              <label>Message pour le client :</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Expliquez pourquoi ce véhicule correspond..."
                rows={4}
                style={{ width: '100%', marginTop: '8px' }}
              />
            </div>
          )}

          {/* Actions */}
          <div className="modal-actions" style={{ marginTop: '20px' }}>
            <button onClick={onClose} className="btn-secondary">
              Annuler
            </button>
            <button 
              onClick={handlePropose} 
              disabled={!selectedVehicle || !message.trim()}
              className="btn-primary"
            >
              ➕ Proposer
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}