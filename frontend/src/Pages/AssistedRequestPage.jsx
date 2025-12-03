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
  const { data: myRequests, mutate } = useSWR('/assisted/requests/me', () => getMyRequests())

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
      'EN_ATTENTE': { text: 'En attente', style: 'status-pending' },
      'EN_COURS': { text: 'En cours', style: 'status-active' },
      'TERMINEE': { text: 'Terminée', style: 'status-completed' },
      'ANNULEE': { text: 'Annulée', style: 'status-cancelled' }
    }
    return badges[status] || badges['EN_ATTENTE']
  }

  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    })
  }

  return (
    <div className="app-main">
      {/* Hero Header */}
      <div style={{
        background: 'var(--white)',
        padding: 'var(--space-12) var(--space-8)',
        marginBottom: 'var(--space-12)',
        border: '1px solid var(--border-light)',
        boxShadow: 'var(--shadow-gloss-md)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '200px',
          background: 'var(--gloss-overlay)',
          pointerEvents: 'none'
        }} />

        <div style={{ position: 'relative', zIndex: 1, maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
          <h1 style={{
            fontSize: '40px',
            fontWeight: 'var(--font-weight-bold)',
            color: 'var(--text-primary)',
            marginBottom: 'var(--space-3)',
            letterSpacing: '-0.03em'
          }}>
            Recherche Assistée
          </h1>
          <p style={{
            fontSize: '18px',
            color: 'var(--text-secondary)',
            lineHeight: '1.6',
            marginBottom: 0
          }}>
            Confiez votre recherche à nos experts automobiles. Nous trouvons le véhicule parfait selon vos critères.
          </p>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))',
        gap: 'var(--space-8)',
        maxWidth: 'var(--container-2xl)',
        margin: '0 auto'
      }}>
        {/* Formulaire de demande */}
        <div className="card" style={{ height: 'fit-content' }}>
          <div className="card-header">
            <h2 className="card-title">Nouvelle Demande</h2>
          </div>

          {success && (
            <div className="success-message" style={{ marginBottom: 'var(--space-5)' }}>
              Demande créée avec succès. Un expert va la traiter prochainement.
            </div>
          )}

          {error && (
            <div className="error-message" style={{ marginBottom: 'var(--space-5)' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Description de votre recherche</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Décrivez précisément le type de véhicule recherché, son usage prévu, vos contraintes..."
                rows={5}
                required
                minLength={10}
                style={{ fontFamily: 'var(--font-primary)' }}
              />
              <small style={{
                display: 'block',
                marginTop: 'var(--space-2)',
                color: 'var(--text-muted)',
                fontSize: '13px'
              }}>
                Plus la description est détaillée, plus nos experts pourront affiner leur recherche.
              </small>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: 'var(--space-4)'
            }}>
              <div className="form-group">
                <label>Budget Maximum (€)</label>
                <input
                  type="number"
                  value={formData.budget_max}
                  onChange={(e) => setFormData({...formData, budget_max: e.target.value})}
                  placeholder="15000"
                  min="0"
                />
              </div>

              <div className="form-group">
                <label>Kilométrage Max (km)</label>
                <input
                  type="number"
                  value={formData.max_mileage}
                  onChange={(e) => setFormData({...formData, max_mileage: e.target.value})}
                  placeholder="100000"
                  min="0"
                />
              </div>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: 'var(--space-4)'
            }}>
              <div className="form-group">
                <label>Carburant</label>
                <select
                  value={formData.preferred_fuel_type}
                  onChange={(e) => setFormData({...formData, preferred_fuel_type: e.target.value})}
                >
                  <option value="">Tous types</option>
                  <option value="essence">Essence</option>
                  <option value="diesel">Diesel</option>
                  <option value="electrique">Électrique</option>
                  <option value="hybride">Hybride</option>
                </select>
              </div>

              <div className="form-group">
                <label>Transmission</label>
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
              <label>Année Minimum</label>
              <input
                type="number"
                value={formData.min_year}
                onChange={(e) => setFormData({...formData, min_year: e.target.value})}
                placeholder="2018"
                min="1980"
                max={new Date().getFullYear() + 1}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: 'var(--space-4)' }}
            >
              {loading ? 'Envoi en cours...' : 'Envoyer la demande'}
            </button>
          </form>
        </div>

        {/* Historique des demandes */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Historique des Demandes</h2>
          </div>

          {!myRequests ? (
            <div className="loading-spinner">
              <div className="spinner"></div>
            </div>
          ) : myRequests.length === 0 ? (
            <div className="empty-state">
              <h3>Aucune demande</h3>
              <p>Créez votre première demande pour bénéficier de l'expertise de nos conseillers.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              {myRequests.map(request => {
                const badge = getStatusBadge(request.status)

                return (
                  <div
                    key={request.id}
                    style={{
                      padding: 'var(--space-5)',
                      background: 'var(--gray-50)',
                      border: '1px solid var(--border-light)',
                      transition: 'all var(--transition-base)',
                      cursor: 'pointer',
                      position: 'relative',
                      overflow: 'hidden'
                    }}
                    onClick={() => navigate(`/assisted/${request.id}`)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = 'var(--border-medium)'
                      e.currentTarget.style.transform = 'translateY(-2px)'
                      e.currentTarget.style.boxShadow = 'var(--shadow-md)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = 'var(--border-light)'
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = 'none'
                    }}
                  >
                    {/* Header */}
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: 'var(--space-3)'
                    }}>
                      <span style={{
                        padding: 'var(--space-1) var(--space-3)',
                        background: badge.style === 'status-pending' ? 'var(--gray-200)' :
                                   badge.style === 'status-active' ? '#FFF7ED' :
                                   badge.style === 'status-completed' ? 'rgba(5, 150, 105, 0.08)' :
                                   'var(--red-accent-light)',
                        color: badge.style === 'status-pending' ? 'var(--text-secondary)' :
                               badge.style === 'status-active' ? '#D97706' :
                               badge.style === 'status-completed' ? '#059669' :
                               'var(--red-accent)',
                        fontSize: '12px',
                        fontWeight: 'var(--font-weight-semibold)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em'
                      }}>
                        {badge.text}
                      </span>

                      <span style={{
                        fontSize: '13px',
                        color: 'var(--text-muted)',
                        fontWeight: 'var(--font-weight-medium)'
                      }}>
                        {formatDate(request.created_at)}
                      </span>
                    </div>

                    {/* Description */}
                    <p style={{
                      fontSize: '15px',
                      lineHeight: '1.6',
                      color: 'var(--text-secondary)',
                      marginBottom: 'var(--space-4)',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical'
                    }}>
                      {request.description}
                    </p>

                    {/* Informations */}
                    <div style={{
                      display: 'flex',
                      gap: 'var(--space-6)',
                      flexWrap: 'wrap',
                      marginBottom: 'var(--space-4)',
                      paddingTop: 'var(--space-3)',
                      borderTop: '1px solid var(--border-light)'
                    }}>
                      {request.budget_max && (
                        <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                          <span style={{
                            fontWeight: 'var(--font-weight-medium)',
                            color: 'var(--text-primary)',
                            marginRight: 'var(--space-2)'
                          }}>
                            Budget
                          </span>
                          {request.budget_max.toLocaleString('fr-FR')} €
                        </div>
                      )}

                      {request.max_mileage && (
                        <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                          <span style={{
                            fontWeight: 'var(--font-weight-medium)',
                            color: 'var(--text-primary)',
                            marginRight: 'var(--space-2)'
                          }}>
                            Kilométrage
                          </span>
                          {request.max_mileage.toLocaleString('fr-FR')} km
                        </div>
                      )}

                      {request.preferred_fuel_type && (
                        <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                          <span style={{
                            fontWeight: 'var(--font-weight-medium)',
                            color: 'var(--text-primary)',
                            marginRight: 'var(--space-2)'
                          }}>
                            Carburant
                          </span>
                          {request.preferred_fuel_type.charAt(0).toUpperCase() + request.preferred_fuel_type.slice(1)}
                        </div>
                      )}
                    </div>

                    {/* CTA */}
                    <div style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 'var(--space-2)',
                      color: 'var(--red-accent)',
                      fontSize: '14px',
                      fontWeight: 'var(--font-weight-medium)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em'
                    }}>
                      Voir les détails
                      <span style={{ fontSize: '12px' }}>→</span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
