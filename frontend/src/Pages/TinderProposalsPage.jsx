import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function getNextProposal(requestId, token) {
  const response = await fetch(`${API_BASE}/api/assisted/requests/${requestId}/tinder/next`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  if (!response.ok) throw new Error('Failed to fetch proposal');
  return response.json();
}

async function tinderAction(proposalId, action, feedback, token) {
  const response = await fetch(`${API_BASE}/api/assisted/proposals/${proposalId}/tinder/${action}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ feedback })
  });
  if (!response.ok) throw new Error(`Failed to ${action}`);
  return response.json();
}

export default function TinderProposalsPage() {
  const { requestId } = useParams();
  const navigate = useNavigate();

  const [proposal, setProposal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showFeedbackModal, setShowFeedbackModal] = useState(null);
  const [feedback, setFeedback] = useState('');
  const [animating, setAnimating] = useState(false);
  const [animationDirection, setAnimationDirection] = useState(null);

  const token = localStorage.getItem('token') || localStorage.getItem('access_token');

  useEffect(() => {
    loadNextProposal();
  }, [requestId]);

  async function loadNextProposal() {
    try {
      setLoading(true);
      const data = await getNextProposal(requestId, token);
      setProposal(data);
    } catch (error) {
      console.error('Error loading proposal:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleAction(action) {
    if (!proposal) return;

    setAnimating(true);
    setAnimationDirection(action === 'reject' ? 'left' : 'right');

    setTimeout(async () => {
      try {
        await tinderAction(proposal.id, action, feedback, token);
        setFeedback('');
        setShowFeedbackModal(null);
        setAnimating(false);
        setAnimationDirection(null);
        await loadNextProposal();
      } catch (error) {
        console.error(`Error during ${action}:`, error);
        setAnimating(false);
        setAnimationDirection(null);
      }
    }, 500);
  }

  function openFeedbackModal(action) {
    setShowFeedbackModal(action);
  }

  function confirmAction() {
    if (showFeedbackModal) {
      handleAction(showFeedbackModal);
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
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
          <p style={{ color: '#666666' }}>Chargement...</p>
        </div>
      </div>
    );
  }

  if (!proposal) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '80vh'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '80px', marginBottom: '24px' }}>🎉</div>
          <h2 style={{
            margin: '0 0 16px 0',
            fontSize: '24px',
            color: '#222222'
          }}>
            Plus de propositions à évaluer !
          </h2>
          <p style={{
            color: '#666666',
            marginBottom: '24px'
          }}>
            Vous avez consulté toutes les propositions de votre expert.
          </p>
          <button
            onClick={() => navigate(`/assisted/requests/${requestId}`)}
            style={{
              padding: '12px 24px',
              background: '#DC2626',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'background 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = '#B91C1C'}
            onMouseLeave={(e) => e.currentTarget.style.background = '#DC2626'}
          >
            Voir toutes mes propositions
          </button>
        </div>
      </div>
    );
  }

  const vehicle = proposal.vehicle;

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
            background: 'white',
            border: '1px solid #EEEEEE',
            padding: '8px 16px',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            color: '#222222',
            fontWeight: 500,
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = '#222222';
            e.currentTarget.style.background = '#FAFAFA';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = '#EEEEEE';
            e.currentTarget.style.background = 'white';
          }}
        >
          ← Retour
        </button>

        <div style={{
          background: '#222222',
          padding: '6px 14px',
          borderRadius: '4px',
          color: 'white',
          fontSize: '12px',
          fontWeight: 600,
          letterSpacing: '0.5px',
          textTransform: 'uppercase'
        }}>
          Mode Sélection
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
            borderRadius: '12px',
            boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
            border: '1px solid #EEEEEE',
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
                  {vehicle.price?.toLocaleString()} €
                </div>
              </div>
            </div>
          ) : (
            <div style={{
              height: '400px',
              background: '#FAFAFA',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#CCCCCC',
              fontSize: '60px'
            }}>
              🚗
            </div>
          )}

          {/* Vehicle Info */}
          <div style={{ padding: '24px' }}>
            {/* Expert Message */}
            {proposal.message && (
              <div style={{
                background: '#FAFAFA',
                padding: '16px',
                borderRadius: '8px',
                marginBottom: '20px',
                border: '1px solid #EEEEEE'
              }}>
                <div style={{
                  fontSize: '12px',
                  fontWeight: 600,
                  color: '#222222',
                  marginBottom: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  <span>💬</span>
                  <span>Message de votre expert</span>
                </div>
                <p style={{
                  margin: 0,
                  fontSize: '14px',
                  lineHeight: 1.6,
                  color: '#666666'
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
                background: '#FAFAFA',
                borderRadius: '8px',
                border: '1px solid #EEEEEE'
              }}>
                <div style={{
                  fontSize: '12px',
                  fontWeight: 600,
                  marginBottom: '8px',
                  color: '#222222',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Description
                </div>
                <p style={{
                  margin: 0,
                  fontSize: '14px',
                  lineHeight: 1.6,
                  color: '#666666'
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
            border: '2px solid #999999',
            color: '#999999',
            fontSize: '32px',
            cursor: animating ? 'not-allowed' : 'pointer',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
            transition: 'all 0.2s',
            opacity: animating ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          onMouseEnter={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.background = '#999999';
              e.currentTarget.style.color = 'white';
            }
          }}
          onMouseLeave={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.background = 'white';
              e.currentTarget.style.color = '#999999';
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
            border: '2px solid #222222',
            color: '#222222',
            fontSize: '36px',
            cursor: animating ? 'not-allowed' : 'pointer',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
            transition: 'all 0.2s',
            opacity: animating ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          onMouseEnter={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.background = '#222222';
              e.currentTarget.style.color = 'white';
            }
          }}
          onMouseLeave={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.background = 'white';
              e.currentTarget.style.color = '#222222';
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
            border: '2px solid #DC2626',
            color: '#DC2626',
            fontSize: '32px',
            cursor: animating ? 'not-allowed' : 'pointer',
            boxShadow: '0 2px 8px rgba(220, 38, 38, 0.15)',
            transition: 'all 0.2s',
            opacity: animating ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          onMouseEnter={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.background = '#DC2626';
              e.currentTarget.style.color = 'white';
            }
          }}
          onMouseLeave={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.background = 'white';
              e.currentTarget.style.color = '#DC2626';
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
        <div style={{
          width: '70px',
          textAlign: 'center',
          fontSize: '11px',
          color: '#999999',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          Refuser
        </div>
        <div style={{
          width: '80px',
          textAlign: 'center',
          fontSize: '11px',
          color: '#999999',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          J'aime
        </div>
        <div style={{
          width: '70px',
          textAlign: 'center',
          fontSize: '11px',
          color: '#999999',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
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
            setShowFeedbackModal(null);
            setFeedback('');
          }}
          onConfirm={confirmAction}
        />
      )}
    </div>
  );
}

function SpecItem({ icon, label, value }) {
  return (
    <div>
      <div style={{
        fontSize: '11px',
        color: '#999999',
        marginBottom: '4px',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.5px'
      }}>
        {icon} {label}
      </div>
      <div style={{
        fontSize: '16px',
        fontWeight: 600,
        color: '#222222'
      }}>
        {value || 'N/A'}
      </div>
    </div>
  );
}

function FeedbackModal({ action, feedback, onFeedbackChange, onClose, onConfirm }) {
  const actionConfig = {
    'like': {
      title: 'J\'aime cette proposition',
      color: '#222222',
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
      title: 'Coup de cœur !',
      color: '#DC2626',
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
      title: 'Refuser cette proposition',
      color: '#999999',
      placeholder: 'Pourquoi ce véhicule ne vous convient pas ?',
      suggestions: [
        'Prix trop élevé',
        'Trop de kilométrage',
        'Pas le bon modèle',
        'Mauvaise localisation',
        'Année trop ancienne'
      ]
    }
  };

  const config = actionConfig[action];

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
          borderRadius: '12px',
          padding: '28px',
          maxWidth: '500px',
          width: '100%',
          boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{
          margin: '0 0 16px 0',
          fontSize: '20px',
          color: config.color,
          fontWeight: 600
        }}>
          {config.title}
        </h2>

        <p style={{
          color: '#666666',
          fontSize: '14px',
          marginBottom: '16px',
          lineHeight: 1.6
        }}>
          Votre feedback aide l'expert à mieux comprendre vos préférences.
          {action === 'reject' && ' (Requis pour refuser)'}
        </p>

        {/* Suggestions */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{
            fontSize: '12px',
            fontWeight: 600,
            marginBottom: '8px',
            color: '#222222',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Suggestions rapides :
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {config.suggestions.map(s => (
              <button
                key={s}
                onClick={() => onFeedbackChange(s)}
                style={{
                  padding: '8px 14px',
                  background: feedback === s ? config.color : '#FAFAFA',
                  color: feedback === s ? 'white' : '#222222',
                  border: feedback === s ? 'none' : '1px solid #EEEEEE',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (feedback !== s) {
                    e.currentTarget.style.background = '#EEEEEE';
                  }
                }}
                onMouseLeave={(e) => {
                  if (feedback !== s) {
                    e.currentTarget.style.background = '#FAFAFA';
                  }
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
            border: '1px solid #EEEEEE',
            borderRadius: '8px',
            fontSize: '14px',
            fontFamily: 'inherit',
            minHeight: '80px',
            resize: 'vertical',
            marginBottom: '20px',
            boxSizing: 'border-box',
            color: '#222222'
          }}
        />

        {/* Actions */}
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={onClose}
            style={{
              flex: 1,
              padding: '14px',
              background: 'white',
              border: '1px solid #EEEEEE',
              borderRadius: '8px',
              fontSize: '15px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
              color: '#222222'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#FAFAFA';
              e.currentTarget.style.borderColor = '#222222';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'white';
              e.currentTarget.style.borderColor = '#EEEEEE';
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
              background: (action === 'reject' && !feedback.trim()) ? '#CCCCCC' : config.color,
              border: 'none',
              color: 'white',
              borderRadius: '8px',
              fontSize: '15px',
              fontWeight: 600,
              cursor: (action === 'reject' && !feedback.trim()) ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              if (!(action === 'reject' && !feedback.trim())) {
                e.currentTarget.style.opacity = '0.9';
              }
            }}
            onMouseLeave={(e) => {
              if (!(action === 'reject' && !feedback.trim())) {
                e.currentTarget.style.opacity = '1';
              }
            }}
          >
            Confirmer
          </button>
        </div>
      </div>
    </div>
  );
}
