import React from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function ProfilePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  if (!user) {
    return (
      <div className="app-main">
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      </div>
    )
  }

  const getRoleInfo = () => {
    const roles = {
      PRO: { label: 'Professionnel', color: 'var(--red-accent)' },
      PARTICULAR: { label: 'Particulier', color: 'var(--gray-700)' },
      EXPERT: { label: 'Expert', color: 'var(--gray-900)' },
      ADMIN: { label: 'Administrateur', color: 'var(--red-accent)' },
    }
    return roles[user.role] || roles.PARTICULAR
  }

  const roleInfo = getRoleInfo()

  return (
    <div className="app-main">
      <div style={{
        maxWidth: 'var(--container-xl)',
        margin: '0 auto'
      }}>
        {/* Header Section */}
        <div style={{
          background: 'var(--white)',
          border: '1px solid var(--border-light)',
          boxShadow: 'var(--shadow-gloss-md)',
          padding: 'var(--space-8)',
          marginBottom: 'var(--space-6)',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-6)',
          flexWrap: 'wrap',
          position: 'relative',
          overflow: 'hidden'
        }}>
          {/* Gloss overlay */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '100px',
            background: 'var(--gloss-overlay)',
            pointerEvents: 'none'
          }} />

          {/* Avatar */}
          <div style={{
            width: '100px',
            height: '100px',
            background: roleInfo.color,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '48px',
            fontWeight: 'var(--font-weight-bold)',
            color: 'var(--white)',
            boxShadow: 'var(--shadow-gloss-md)',
            position: 'relative',
            zIndex: 1
          }}>
            {user.full_name?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase() || '?'}
          </div>

          {/* User Info */}
          <div style={{ flex: 1, position: 'relative', zIndex: 1 }}>
            <h1 style={{
              fontSize: '32px',
              fontWeight: 'var(--font-weight-bold)',
              color: 'var(--text-primary)',
              margin: '0 0 var(--space-2) 0',
              letterSpacing: '-0.02em'
            }}>
              {user.full_name || 'Utilisateur'}
            </h1>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-3)',
              marginBottom: 'var(--space-3)',
              flexWrap: 'wrap'
            }}>
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                background: roleInfo.color,
                color: 'var(--white)',
                padding: 'var(--space-1) var(--space-3)',
                fontSize: '12px',
                fontWeight: 'var(--font-weight-semibold)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>
                {roleInfo.label}
              </span>

              {user.is_verified ? (
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  background: 'rgba(5, 150, 105, 0.1)',
                  color: '#059669',
                  padding: 'var(--space-1) var(--space-3)',
                  fontSize: '12px',
                  fontWeight: 'var(--font-weight-semibold)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  Vérifié
                </span>
              ) : (
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  background: 'rgba(245, 158, 11, 0.1)',
                  color: '#D97706',
                  padding: 'var(--space-1) var(--space-3)',
                  fontSize: '12px',
                  fontWeight: 'var(--font-weight-semibold)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  En attente
                </span>
              )}
            </div>
            <p style={{
              fontSize: '14px',
              color: 'var(--text-secondary)',
              margin: 0,
              fontWeight: 'var(--font-weight-medium)'
            }}>
              Membre depuis le {new Date(user.created_at).toLocaleDateString('fr-FR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
              })}
            </p>
          </div>
        </div>

        {/* Information Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 'var(--space-5)',
          marginBottom: 'var(--space-6)'
        }}>
          {/* Contact Info Card */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Informations de contact</h3>
            </div>
            <div className="card-body">
              <InfoField label="Email" value={user.email} />
              <InfoField label="Téléphone" value={user.phone || 'Non renseigné'} />
            </div>
          </div>

          {/* Account Info Card */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Sécurité</h3>
            </div>
            <div className="card-body">
              <InfoField
                label="ID Utilisateur"
                value={user.id.substring(0, 8) + '...'}
              />
              <InfoField
                label="Compte créé"
                value={new Date(user.created_at).toLocaleDateString('fr-FR')}
              />
            </div>
          </div>
        </div>

        {/* Actions Card */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Actions du compte</h3>
          </div>
          <div className="card-body">
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: 'var(--space-3)'
            }}>
              <button
                onClick={() => navigate('/messages')}
                className="btn btn-primary"
                style={{
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  fontSize: '14px'
                }}
              >
                Mes messages
              </button>

              {user.role !== 'EXPERT' && (
                <button
                  onClick={() => navigate('/favorites')}
                  className="btn btn-secondary"
                  style={{
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    fontSize: '14px'
                  }}
                >
                  Mes favoris
                </button>
              )}

              <button
                onClick={handleLogout}
                style={{
                  padding: 'var(--space-3) var(--space-4)',
                  background: 'var(--red-accent)',
                  color: 'var(--white)',
                  border: 'none',
                  fontSize: '14px',
                  fontWeight: 'var(--font-weight-semibold)',
                  cursor: 'pointer',
                  transition: 'all var(--transition-base)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  position: 'relative',
                  overflow: 'hidden'
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)'
                  e.target.style.boxShadow = 'var(--shadow-md)'
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)'
                  e.target.style.boxShadow = 'none'
                }}
              >
                Déconnexion
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function InfoField({ label, value }) {
  return (
    <div style={{
      marginBottom: 'var(--space-4)',
      paddingBottom: 'var(--space-4)',
      borderBottom: '1px solid var(--border-light)'
    }}>
      <div style={{
        fontSize: '12px',
        fontWeight: 'var(--font-weight-semibold)',
        color: 'var(--text-secondary)',
        marginBottom: 'var(--space-2)',
        textTransform: 'uppercase',
        letterSpacing: '0.05em'
      }}>
        {label}
      </div>
      <div style={{
        fontSize: '15px',
        color: 'var(--text-primary)',
        fontWeight: 'var(--font-weight-medium)'
      }}>
        {value}
      </div>
    </div>
  )
}
