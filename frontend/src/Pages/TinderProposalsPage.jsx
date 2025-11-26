import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

// TODO: Remplacer par vos vrais appels API
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function getNextProposal(requestId, token) {
  const response = await fetch(`${API_BASE}/api/assisted/requests/${requestId}/tinder/next`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  if (!response.ok) throw new Error('Failed to fetch proposal')
  return response.json()
}

async function tinderAction(proposalId, action, feedback, token) {
  const response = await fetch(`${API_BASE}/api/assisted/proposals/${proposalId}/tinder/${action}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ feedback })
  })
  if (!response.ok) throw new Error(`Failed to ${action}`)
  return response.json()
}

export default function TinderProposalsPage() {
  const { requestId } = useParams()
  const navigate = useNavigate()

  const [proposal, setProposal] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showFeedbackModal, setShowFeedbackModal] = useState(null) // 'like', 'super-like', or 'reject'
  const [feedback, setFeedback] = useState('')
  const [animating, setAnimating] = useState(false)
  const [animationDirection, setAnimationDirection] = useState(null) // 'left' or 'right'

  // TODO: Récupérer le token d'auth depuis votre AuthContext
  const token = localStorage.getItem('token')

  useEffect(() => {
    loadNextProposal()
  }, [requestId])

  async function loadNextProposal() {
    try {
      setLoading(true)
      const data = await getNextProposal(requestId, token)
      setProposal(data)
    } catch (error) {
      console.error('Error loading proposal:', error)
    } finally {
      setLoading(false)
    }
  }

  async function handleAction(action) {
    if (!proposal) return

    // Animation de swipe
    setAnimating(true)
    setAnimationDirection(action === 'reject' ? 'left' : 'right')

    // Attendre la fin de l'animation
    setTimeout(async () => {
      try {
        await tinderAction(proposal.id, action, feedback, token)
        setFeedback('')
        setShowFeedbackModal(null)
        setAnimating(false)
        setAnimationDirection(null)

        // Charger la proposition suivante
        await loadNextProposal()
      } catch (error) {
        console.error(`Error during ${action}:`, error)
        setAnimating(false)
        setAnimationDirection(null)
      }
    }, 500)
  }

  function openFeedbackModal(action) {
    setShowFeedbackModal(action)
  }

  function confirmAction() {
    if (showFeedbackModal) {
      handleAction(showFeedbackModal)
    }
  }

  if (loading && !proposal) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '80vh'
      }}>
        <div style={{textAlign: 'center'}}>
          <div style={{fontSize: '48px', marginBottom: '16px'}}>⏳</div>
          <p>Chargement...</p>
        </div>
      </div>
    )
  }

  if (!proposal) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '80vh'
      }}>
        <div style={{textAlign: 'center'}}>
          <div style={{fontSize: '80px', marginBottom: '24px'}}>🎉</div>
          <h2 style={{margin: '0 0 16px 0', fontSize: '24px'}}>
            Plus de propositions à évaluer !
          </h2>
          <p style={{color: '#6a737d', marginBottom: '24px'}}>
            Vous avez consulté toutes les propositions de votre expert.
          </p>
          <button
            onClick={() => navigate(`/assisted/requests/${requestId}`)}
            style={{
              padding: '12px 24px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Voir toutes mes propositions
          </button>
        </div>
      </div>
    )
  }

  const vehicle = proposal.vehicle

  return (
    <div style={{
      maxWidth: '600px',
      margin: '0 auto',
      padding: '20px',
      minHeight: '100vh'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '30px'
      }}>
        <button
          onClick={() => navigate(`/assisted/requests/${requestId}`)}
          style={{
            background: 'none',
            border: '1px solid #ddd',
            padding: '8px 16px',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          ← Retour
        </button>

        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          padding: '8px 16px',
          borderRadius: '20px',
          color: 'white',
          fontSize: '14px',
          fontWeight: 600
        }}>
          🔥 Mode Tinder
        </div>
      </div>

      {/* Card Container */}
      <div style={{
        perspective: '1000px',
        marginBottom: '30px'
      }}>
        <div
          style={{
            background: 'white',
            borderRadius: '24px',
            boxShadow: '0 10px 40px rgba(0,0,0,0.15)',
            overflow: 'hidden',
            transform: animating
              ? `translateX(${animationDirection === 'left' ? '-150%' : '150%'}) rotate(${animationDirection === 'left' ? '-30deg' : '30deg'})`
              : 'translateX(0) rotate(0)',
            transition: 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)',
            opacity: animating ? 0 : 1
          }}
        >
          {/* Vehicle Image */}
          {vehicle.images && vehicle.images.length > 0 ? (
            <div style={{
              height: '400px',
              background: `linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.3)), url(${vehicle.images[0]})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              position: 'relative'
            }}>
              <div style={{
                position: 'absolute',
                bottom: '20px',
                left: '20px',
                right: '20px',
                color: 'white'
              }}>
                <h1 style={{
                  margin: '0 0 8px 0',
                  fontSize: '28px',
                  fontWeight: 700,
                  textShadow: '0 2px 10px rgba(0,0,0,0.5)'
                }}>
                  {vehicle.title}
                </h1>
                <div style={{
                  fontSize: '20px',
                  fontWeight: 600,
                  textShadow: '0 2px 10px rgba(0,0,0,0.5)'
                }}>
                  💰 {vehicle.price?.toLocaleString()} €
                </div>
              </div>
            </div>
          ) : (
            <div style={{
              height: '400px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '60px'
            }}>
              🚗
            </div>
          )}

          {/* Vehicle Info */}
          <div style={{padding: '24px'}}>
            {/* Expert Message */}
            {proposal.message && (
              <div style={{
                background: '#e7f3ff',
                padding: '16px',
                borderRadius: '12px',
                marginBottom: '20px'
              }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: 600,
                  color: '#667eea',
                  marginBottom: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>💬</span>
                  <span>Message de votre expert</span>
                </div>
                <p style={{
                  margin: 0,
                  fontSize: '14px',
                  lineHeight: 1.6,
                  color: '#24292e'
                }}>
                  {proposal.message}
                </p>
              </div>
            )}

            {/* Specs Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '16px'
            }}>
              <SpecItem icon="📅" label="Année" value={vehicle.year} />
              <SpecItem icon="🛣️" label="Kilométrage" value={`${vehicle.mileage?.toLocaleString()} km`} />
              <SpecItem icon="⛽" label="Carburant" value={vehicle.fuel_type} />
              <SpecItem icon="⚙️" label="Transmission" value={vehicle.transmission} />
              {vehicle.location_city && (
                <SpecItem icon="📍" label="Localisation" value={vehicle.location_city} />
              )}
            </div>

            {/* Description */}
            {vehicle.description && (
              <div style={{
                marginTop: '20px',
                padding: '16px',
                background: '#f8f9fa',
                borderRadius: '12px'
              }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: 600,
                  marginBottom: '8px'
                }}>
                  📝 Description
                </div>
                <p style={{
                  margin: 0,
                  fontSize: '14px',
                  lineHeight: 1.6,
                  color: '#6a737d'
                }}>
                  {vehicle.description}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '20px'
      }}>
        {/* Reject Button */}
        <button
          onClick={() => openFeedbackModal('reject')}
          disabled={animating}
          style={{
            width: '70px',
            height: '70px',
            borderRadius: '50%',
            background: 'white',
            border: '3px solid #dc3545',
            color: '#dc3545',
            fontSize: '32px',
            cursor: animating ? 'not-allowed' : 'pointer',
            boxShadow: '0 4px 12px rgba(220, 53, 69, 0.3)',
            transition: 'all 0.2s',
            opacity: animating ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          onMouseEnter={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1.1)'
              e.currentTarget.style.background = '#dc3545'
              e.currentTarget.style.color = 'white'
            }
          }}
          onMouseLeave={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1)'
              e.currentTarget.style.background = 'white'
              e.currentTarget.style.color = '#dc3545'
            }
          }}
        >
          ❌
        </button>

        {/* Like Button */}
        <button
          onClick={() => openFeedbackModal('like')}
          disabled={animating}
          style={{
            width: '80px',
            height: '80px',
            borderRadius: '50%',
            background: 'white',
            border: '3px solid #28a745',
            color: '#28a745',
            fontSize: '36px',
            cursor: animating ? 'not-allowed' : 'pointer',
            boxShadow: '0 4px 12px rgba(40, 167, 69, 0.3)',
            transition: 'all 0.2s',
            opacity: animating ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          onMouseEnter={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1.1)'
              e.currentTarget.style.background = '#28a745'
              e.currentTarget.style.color = 'white'
            }
          }}
          onMouseLeave={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1)'
              e.currentTarget.style.background = 'white'
              e.currentTarget.style.color = '#28a745'
            }
          }}
        >
          👍
        </button>

        {/* Super Like Button */}
        <button
          onClick={() => openFeedbackModal('super-like')}
          disabled={animating}
          style={{
            width: '70px',
            height: '70px',
            borderRadius: '50%',
            background: 'white',
            border: '3px solid #e91e63',
            color: '#e91e63',
            fontSize: '32px',
            cursor: animating ? 'not-allowed' : 'pointer',
            boxShadow: '0 4px 12px rgba(233, 30, 99, 0.3)',
            transition: 'all 0.2s',
            opacity: animating ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          onMouseEnter={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1.1)'
              e.currentTarget.style.background = '#e91e63'
              e.currentTarget.style.color = 'white'
            }
          }}
          onMouseLeave={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1)'
              e.currentTarget.style.background = 'white'
              e.currentTarget.style.color = '#e91e63'
            }
          }}
        >
          ❤️
        </button>
      </div>

      {/* Button Labels */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '20px',
        marginTop: '12px'
      }}>
        <div style={{width: '70px', textAlign: 'center', fontSize: '12px', color: '#6a737d', fontWeight: 600}}>
          Refuser
        </div>
        <div style={{width: '80px', textAlign: 'center', fontSize: '12px', color: '#6a737d', fontWeight: 600}}>
          J'aime
        </div>
        <div style={{width: '70px', textAlign: 'center', fontSize: '12px', color: '#6a737d', fontWeight: 600}}>
          Coup de ❤️
        </div>
      </div>

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <FeedbackModal
          action={showFeedbackModal}
          feedback={feedback}
          onFeedbackChange={setFeedback}
          onClose={() => {
            setShowFeedbackModal(null)
            setFeedback('')
          }}
          onConfirm={confirmAction}
        />
      )}
    </div>
  )
}

// Spec Item Component
function SpecItem({ icon, label, value }) {
  return (
    <div>
      <div style={{
        fontSize: '12px',
        color: '#6a737d',
        marginBottom: '4px',
        fontWeight: 600
      }}>
        {icon} {label}
      </div>
      <div style={{
        fontSize: '16px',
        fontWeight: 600,
        color: '#24292e'
      }}>
        {value || 'N/A'}
      </div>
    </div>
  )
}

// Feedback Modal Component
function FeedbackModal({ action, feedback, onFeedbackChange, onClose, onConfirm }) {
  const actionConfig = {
    'like': {
      title: '👍 J\'aime cette proposition',
      color: '#28a745',
      placeholder: 'Qu\'est-ce qui vous plaît dans ce véhicule ? (optionnel)',
      suggestions: [
        'Bon rapport qualité-prix',
        'Kilométrage adapté',
        'Modèle intéressant',
        'Bien localisé',
        'Carburant économique'
      ]
    },
    'super-like': {
      title: '❤️ Coup de foudre !',
      color: '#e91e63',
      placeholder: 'Pourquoi ce véhicule est parfait pour vous ? (optionnel)',
      suggestions: [
        'Exactement ce que je cherchais !',
        'Prix excellent',
        'Correspond parfaitement',
        'Très bon état',
        'Idéal pour mes besoins'
      ]
    },
    'reject': {
      title: '❌ Refuser cette proposition',
      color: '#dc3545',
      placeholder: 'Pourquoi ce véhicule ne vous convient pas ?',
      suggestions: [
        'Prix trop élevé',
        'Trop de kilométrage',
        'Pas le bon modèle',
        'Mauvaise localisation',
        'Année trop ancienne'
      ]
    }
  }

  const config = actionConfig[action]

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
          borderRadius: '20px',
          padding: '28px',
          maxWidth: '500px',
          width: '100%',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{
          margin: '0 0 16px 0',
          fontSize: '22px',
          color: config.color
        }}>
          {config.title}
        </h2>

        <p style={{
          color: '#6a737d',
          fontSize: '14px',
          marginBottom: '16px'
        }}>
          Votre feedback aide l'expert à mieux comprendre vos préférences.
          {action === 'reject' && ' (Requis pour refuser)'}
        </p>

        {/* Suggestions */}
        <div style={{marginBottom: '16px'}}>
          <div style={{
            fontSize: '13px',
            fontWeight: 600,
            marginBottom: '8px',
            color: '#24292e'
          }}>
            Suggestions rapides :
          </div>
          <div style={{display: 'flex', flexWrap: 'wrap', gap: '8px'}}>
            {config.suggestions.map(s => (
              <button
                key={s}
                onClick={() => onFeedbackChange(s)}
                style={{
                  padding: '8px 14px',
                  background: feedback === s ? config.color : '#f0f0f0',
                  color: feedback === s ? 'white' : '#24292e',
                  border: 'none',
                  borderRadius: '20px',
                  fontSize: '12px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Custom feedback */}
        <textarea
          value={feedback}
          onChange={(e) => onFeedbackChange(e.target.value)}
          placeholder={config.placeholder}
          style={{
            width: '100%',
            padding: '12px',
            border: '2px solid #e1e4e8',
            borderRadius: '12px',
            fontSize: '14px',
            fontFamily: 'inherit',
            minHeight: '80px',
            resize: 'vertical',
            marginBottom: '20px',
            boxSizing: 'border-box'
          }}
        />

        {/* Actions */}
        <div style={{display: 'flex', gap: '12px'}}>
          <button
            onClick={onClose}
            style={{
              flex: 1,
              padding: '14px',
              background: 'white',
              border: '2px solid #e1e4e8',
              borderRadius: '10px',
              fontSize: '15px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            Annuler
          </button>
          <button
            onClick={onConfirm}
            disabled={action === 'reject' && !feedback.trim()}
            style={{
              flex: 1,
              padding: '14px',
              background: (action === 'reject' && !feedback.trim()) ? '#ccc' : config.color,
              border: 'none',
              color: 'white',
              borderRadius: '10px',
              fontSize: '15px',
              fontWeight: 600,
              cursor: (action === 'reject' && !feedback.trim()) ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s'
            }}
          >
            Confirmer
          </button>
        </div>
      </div>
    </div>
  )
}
