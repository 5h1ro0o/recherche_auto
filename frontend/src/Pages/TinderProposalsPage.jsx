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
          <div style={{ fontSize: 'var(--space-12)', marginBottom: 'var(--space-4)' }}></div>
          <p style={{ color: 'var(--text-secondary)' }}>Chargement...</p>
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
          <div style={{ fontSize: 'var(--space-20)', marginBottom: 'var(--space-6)' }}></div>
          <h2 style={{
            margin: '0 0 16px 0',
            fontSize: 'var(--space-6)',
            color: 'var(--text-primary)'
          }}>
            Plus de propositions à évaluer !
          </h2>
          <p style={{
            color: 'var(--text-secondary)',
            marginBottom: 'var(--space-6)'
          }}>
            Vous avez consulté toutes les propositions de votre expert.
          </p>
          <button
            onClick={() => navigate(`/assisted/requests/${requestId}`)}
            style={{
              padding: '12px 24px',
              background: 'var(--red-accent)',
              color: 'var(--white)',
              border: 'none',
                            fontSize: 'var(--space-4)',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'background 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'var(--red-accent)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'var(--red-accent)'}
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
      padding: 'var(--space-5)',
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
            background: 'var(--white)',
            border: '1px solid #EEEEEE',
            padding: '8px 16px',
                        cursor: 'pointer',
            fontSize: '14px',
            color: 'var(--text-primary)',
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
          ← Retour
        </button>

        <div style={{
          background: 'var(--text-primary)',
          padding: '6px 14px',
                    color: 'var(--white)',
          fontSize: 'var(--space-3)',
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
            background: 'var(--white)',
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
                bottom: 'var(--space-5)',
                left: 'var(--space-5)',
                right: 'var(--space-5)',
                color: 'var(--white)'
              }}>
                <h1 style={{
                  margin: '0 0 8px 0',
                  fontSize: 'var(--space-7)',
                  fontWeight: 700,
                  textShadow: '0 2px 10px rgba(0,0,0,0.5)'
                }}>
                  {vehicle.title}
                </h1>
                <div style={{
                  fontSize: 'var(--space-5)',
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
              background: 'var(--gray-50)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#CCCCCC',
              fontSize: 'var(--space-16)'
            }}>
              
            </div>
          )}

          {/* Vehicle Info */}
          <div style={{ padding: 'var(--space-6)' }}>
            {/* Expert Message */}
            {proposal.message && (
              <div style={{
                background: 'var(--gray-50)',
                padding: 'var(--space-4)',
                                marginBottom: 'var(--space-5)',
                border: '1px solid #EEEEEE'
              }}>
                <div style={{
                  fontSize: 'var(--space-3)',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  marginBottom: 'var(--space-2)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-2)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  <span></span>
                  <span>Message de votre expert</span>
                </div>
                <p style={{
                  margin: 0,
                  fontSize: '14px',
                  lineHeight: 1.6,
                  color: 'var(--text-secondary)'
                }}>
                  {proposal.message}
                </p>
              </div>
            )}

            {/* Specs Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: 'var(--space-4)'
            }}>
              <SpecItem icon="" label="Année" value={vehicle.year} />
              <SpecItem icon="" label="Kilométrage" value={`${vehicle.mileage?.toLocaleString()} km`} />
              <SpecItem icon="" label="Carburant" value={vehicle.fuel_type} />
              <SpecItem icon="" label="Transmission" value={vehicle.transmission} />
              {vehicle.location_city && (
                <SpecItem icon="" label="Localisation" value={vehicle.location_city} />
              )}
            </div>

            {/* Description */}
            {vehicle.description && (
              <div style={{
                marginTop: 'var(--space-5)',
                padding: 'var(--space-4)',
                background: 'var(--gray-50)',
                                border: '1px solid #EEEEEE'
              }}>
                <div style={{
                  fontSize: 'var(--space-3)',
                  fontWeight: 600,
                  marginBottom: 'var(--space-2)',
                  color: 'var(--text-primary)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Description
                </div>
                <p style={{
                  margin: 0,
                  fontSize: '14px',
                  lineHeight: 1.6,
                  color: 'var(--text-secondary)'
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
        gap: 'var(--space-5)'
      }}>
        {/* Reject Button */}
        <button
          onClick={() => openFeedbackModal('reject')}
          disabled={animating}
          style={{
            width: '70px',
            height: '70px',
            borderRadius: '50%',
            background: 'var(--white)',
            border: '2px solid #999999',
            color: 'var(--text-muted)',
            fontSize: 'var(--space-8)',
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
              e.currentTarget.style.background = 'var(--text-muted)';
              e.currentTarget.style.color = 'var(--white)';
            }
          }}
          onMouseLeave={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.background = 'var(--white)';
              e.currentTarget.style.color = 'var(--text-muted)';
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
            width: 'var(--space-20)',
            height: 'var(--space-20)',
            borderRadius: '50%',
            background: 'var(--white)',
            border: '2px solid #222222',
            color: 'var(--text-primary)',
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
              e.currentTarget.style.background = 'var(--text-primary)';
              e.currentTarget.style.color = 'var(--white)';
            }
          }}
          onMouseLeave={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.background = 'var(--white)';
              e.currentTarget.style.color = 'var(--text-primary)';
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
            background: 'var(--white)',
            border: '2px solid #DC2626',
            color: 'var(--red-accent)',
            fontSize: 'var(--space-8)',
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
              e.currentTarget.style.background = 'var(--red-accent)';
              e.currentTarget.style.color = 'var(--white)';
            }
          }}
          onMouseLeave={(e) => {
            if (!animating) {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.background = 'var(--white)';
              e.currentTarget.style.color = 'var(--red-accent)';
            }
          }}
        >
          
        </button>
      </div>

      {/* Button Labels */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 'var(--space-5)',
        marginTop: 'var(--space-3)'
      }}>
        <div style={{
          width: '70px',
          textAlign: 'center',
          fontSize: '11px',
          color: 'var(--text-muted)',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          Refuser
        </div>
        <div style={{
          width: 'var(--space-20)',
          textAlign: 'center',
          fontSize: '11px',
          color: 'var(--text-muted)',
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
          color: 'var(--text-muted)',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          Coup de 
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
        color: 'var(--text-muted)',
        marginBottom: 'var(--space-1)',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.5px'
      }}>
        {icon} {label}
      </div>
      <div style={{
        fontSize: 'var(--space-4)',
        fontWeight: 600,
        color: 'var(--text-primary)'
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
      color: 'var(--text-primary)',
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
      color: 'var(--red-accent)',
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
      color: 'var(--text-muted)',
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
          boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{
          margin: '0 0 16px 0',
          fontSize: 'var(--space-5)',
          color: config.color,
          fontWeight: 600
        }}>
          {config.title}
        </h2>

        <p style={{
          color: 'var(--text-secondary)',
          fontSize: '14px',
          marginBottom: 'var(--space-4)',
          lineHeight: 1.6
        }}>
          Votre feedback aide l'expert à mieux comprendre vos préférences.
          {action === 'reject' && ' (Requis pour refuser)'}
        </p>

        {/* Suggestions */}
        <div style={{ marginBottom: 'var(--space-4)' }}>
          <div style={{
            fontSize: 'var(--space-3)',
            fontWeight: 600,
            marginBottom: 'var(--space-2)',
            color: 'var(--text-primary)',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Suggestions rapides :
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
            {config.suggestions.map(s => (
              <button
                key={s}
                onClick={() => onFeedbackChange(s)}
                style={{
                  padding: '8px 14px',
                  background: feedback === s ? config.color : 'var(--gray-50)',
                  color: feedback === s ? 'var(--white)' : 'var(--text-primary)',
                  border: feedback === s ? 'none' : '1px solid #EEEEEE',
                                    fontSize: 'var(--space-3)',
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (feedback !== s) {
                    e.currentTarget.style.background = 'var(--border-light)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (feedback !== s) {
                    e.currentTarget.style.background = 'var(--gray-50)';
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
            padding: 'var(--space-3)',
            border: '1px solid #EEEEEE',
                        fontSize: '14px',
            fontFamily: 'inherit',
            minHeight: 'var(--space-20)',
            resize: 'vertical',
            marginBottom: 'var(--space-5)',
            boxSizing: 'border-box',
            color: 'var(--text-primary)'
          }}
        />

        {/* Actions */}
        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <button
            onClick={onClose}
            style={{
              flex: 1,
              padding: '14px',
              background: 'var(--white)',
              border: '1px solid #EEEEEE',
                            fontSize: '15px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
              color: 'var(--text-primary)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--gray-50)';
              e.currentTarget.style.borderColor = 'var(--text-primary)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'var(--white)';
              e.currentTarget.style.borderColor = 'var(--border-light)';
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
              color: 'var(--white)',
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
