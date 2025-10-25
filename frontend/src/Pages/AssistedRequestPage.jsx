// frontend/src/Pages/AssistedRequestPage.jsx
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { createAssistedRequest, getMyRequests } from '../services/assisted'
import useSWR from 'swr'

export default function AssistedRequestPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    description: '',
    budget_max: '',
    preferred_fuel_type: '',
    preferred_transmission: '',
    max_mileage: '',
    min_year: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  // Charger mes demandes existantes
  const { data: myRequests, mutate } = useSWR('/assisted/requests/me', getMyRequests)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Nettoyer les valeurs vides
      const cleanData = {
        description: formData.description,
        budget_max: formData.budget_max ? parseInt(formData.budget_max) : null,
        preferred_fuel_type: formData.preferred_fuel_type || null,
        preferred_transmission: formData.preferred_transmission || null,
        max_mileage: formData.max_mileage ? parseInt(formData.max_mileage) : null,
        min_year: formData.min_year ? parseInt(formData.min_year) : null
      }

      await createAssistedRequest(cleanData)
      setSuccess(true)
      mutate() // Recharger la liste
      
      // Reset form
      setFormData({
        description: '',
        budget_max: '',
        preferred_fuel_type: '',
        preferred_transmission: '',
        max_mileage: '',
        min_year: ''
      })

      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la création')
    } finally {
      setLoading(false)
    }
  }

  function getStatusBadge(status) {
    const badges = {
      'EN_ATTENTE': { text: '⏳ En attente', class: 'status-pending' },
      'EN_COURS': { text: '🔄 En cours', class: 'status-progress' },
      'TERMINEE': { text: '✅ Terminée', class: 'status-completed' },
      'ANNULEE': { text: '❌ Annulée', class: 'status-cancelled' }
    }
    return badges[status] || badges['EN_ATTENTE']
  }

  return (
    <div className="assisted-page">
      <div className="page-header">
        <h1>🤝 Mode Assisté</h1>
        <p className="subtitle">
          Un expert vous aide à trouver le véhicule idéal selon vos critères
        </p>
      </div>

      <div className="assisted-container">
        {/* Formulaire de demande */}
        <div className="request-form-card">
          <h2>Créer une demande</h2>
          
          {success && (
            <div className="success-message">
              ✅ Demande créée avec succès ! Un expert va bientôt la prendre en charge.
            </div>
          )}
          
          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Description de votre recherche *</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Exemple : Je recherche une citadine fiable pour faire du trajet domicile-travail, avec une consommation faible..."
                rows={4}
                required
                minLength={10}
              />
              <small>Soyez le plus précis possible (usage, préférences, contraintes...)</small>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Budget maximum</label>
                <input
                  type="number"
                  value={formData.budget_max}
                  onChange={(e) => setFormData({...formData, budget_max: e.target.value})}
                  placeholder="Ex: 15000"
                  min="0"
                />
              </div>

              <div className="form-group">
                <label>Kilométrage maximum</label>
                <input
                  type="number"
                  value={formData.max_mileage}
                  onChange={(e) => setFormData({...formData, max_mileage: e.target.value})}
                  placeholder="Ex: 100000"
                  min="0"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Carburant préféré</label>
                <select
                  value={formData.preferred_fuel_type}
                  onChange={(e) => setFormData({...formData, preferred_fuel_type: e.target.value})}
                >
                  <option value="">Tous</option>
                  <option value="essence">Essence</option>
                  <option value="diesel">Diesel</option>
                  <option value="electrique">Électrique</option>
                  <option value="hybride">Hybride</option>
                </select>
              </div>

              <div className="form-group">
                <label>Transmission préférée</label>
                <select
                  value={formData.preferred_transmission}
                  onChange={(e) => setFormData({...formData, preferred_transmission: e.target.value})}
                >
                  <option value="">Toutes</option>
                  <option value="manuelle">Manuelle</option>
                  <option value="automatique">Automatique</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Année minimum</label>
              <input
                type="number"
                value={formData.min_year}
                onChange={(e) => setFormData({...formData, min_year: e.target.value})}
                placeholder="Ex: 2018"
                min="1980"
                max={new Date().getFullYear() + 1}
              />
            </div>

            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Envoi en cours...' : '📤 Envoyer ma demande'}
            </button>
          </form>
        </div>

        {/* Liste de mes demandes */}
        <div className="my-requests-card">
          <h2>Mes demandes</h2>
          
          {!myRequests ? (
            <div className="loading">Chargement...</div>
          ) : myRequests.length === 0 ? (
            <div className="empty-state">
              <p>Vous n'avez pas encore de demande</p>
            </div>
          ) : (
            <div className="requests-list">
              {myRequests.map(request => (
                <div key={request.id} className="request-item">
                  <div className="request-header">
                    <span className={`status-badge ${getStatusBadge(request.status).class}`}>
                      {getStatusBadge(request.status).text}
                    </span>
                    <span className="request-date">
                      {new Date(request.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <div className="request-description">
                    {request.description.slice(0, 100)}
                    {request.description.length > 100 && '...'}
                  </div>
                  
                  {request.budget_max && (
                    <div className="request-info">
                      💰 Budget max : {request.budget_max} €
                    </div>
                  )}
                  
                  <button
                    onClick={() => navigate(`/assisted/${request.id}`)}
                    className="btn-view"
                  >
                    👁️ Voir détails
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}