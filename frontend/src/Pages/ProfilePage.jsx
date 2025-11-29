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
      <div style={{
        minHeight: '80vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
          <p style={{ color: '#6B7280' }}>Chargement...</p>
        </div>
      </div>
    )
  }

  const getRoleInfo = () => {
    const roles = {
      PRO: { icon: '🏢', label: 'Professionnel', color: '#DC2626' },
      PARTICULAR: { icon: '👤', label: 'Particulier', color: '#10B981' },
      EXPERT: { icon: '⭐', label: 'Expert', color: '#F59E0B' },
      ADMIN: { icon: '🔧', label: 'Administrateur', color: '#EF4444' },
    }
    return roles[user.role] || roles.PARTICULAR
  }

  const roleInfo = getRoleInfo()

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
      padding: '32px 20px',
    }}>
      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
      }}>
        {/* Header Section */}
        <div style={{
          background: 'white',
          borderRadius: '16px',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
          padding: '32px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          gap: '24px',
          flexWrap: 'wrap',
        }}>
          {/* Avatar */}
          <div style={{
            width: '100px',
            height: '100px',
            borderRadius: '50%',
            background: `linear-gradient(135deg, ${roleInfo.color} 0%, ${roleInfo.color}dd 100%)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '48px',
            fontWeight: 700,
            color: 'white',
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)',
          }}>
            {user.full_name?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase() || '?'}
          </div>

          {/* User Info */}
          <div style={{ flex: 1 }}>
            <h1 style={{
              fontSize: '32px',
              fontWeight: 700,
              color: '#222222',
              margin: '0 0 8px 0',
            }}>
              {user.full_name || 'Utilisateur'}
            </h1>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '12px',
              flexWrap: 'wrap',
            }}>
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                background: roleInfo.color,
                color: 'white',
                padding: '6px 14px',
                borderRadius: '20px',
                fontSize: '14px',
                fontWeight: 600,
              }}>
                <span>{roleInfo.icon}</span>
                <span>{roleInfo.label}</span>
              </span>

              {user.is_verified ? (
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  background: '#10B981',
                  color: 'white',
                  padding: '6px 14px',
                  borderRadius: '20px',
                  fontSize: '14px',
                  fontWeight: 600,
                }}>
                  <span>✅</span>
                  <span>Vérifié</span>
                </span>
              ) : (
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  background: '#F59E0B',
                  color: 'white',
                  padding: '6px 14px',
                  borderRadius: '20px',
                  fontSize: '14px',
                  fontWeight: 600,
                }}>
                  <span>⏳</span>
                  <span>En attente</span>
                </span>
              )}
            </div>
            <p style={{
              fontSize: '14px',
              color: '#6B7280',
              margin: 0,
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
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '20px',
          marginBottom: '24px',
        }}>
          {/* Contact Info Card */}
          <div style={{
            background: 'white',
            borderRadius: '16px',
            boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
            padding: '24px',
          }}>
            <h3 style={{
              fontSize: '18px',
              fontWeight: 600,
              color: '#222222',
              margin: '0 0 20px 0',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}>
              <span>📧</span>
              <span>Informations de contact</span>
            </h3>

            <InfoField label="Email" value={user.email} icon="✉️" />
            <InfoField label="Téléphone" value={user.phone || 'Non renseigné'} icon="📱" />
          </div>

          {/* Account Info Card */}
          <div style={{
            background: 'white',
            borderRadius: '16px',
            boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
            padding: '24px',
          }}>
            <h3 style={{
              fontSize: '18px',
              fontWeight: 600,
              color: '#222222',
              margin: '0 0 20px 0',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}>
              <span>🔐</span>
              <span>Sécurité</span>
            </h3>

            <InfoField
              label="ID Utilisateur"
              value={user.id.substring(0, 8) + '...'}
              icon="🆔"
            />
            <InfoField
              label="Compte créé"
              value={new Date(user.created_at).toLocaleDateString('fr-FR')}
              icon="📅"
            />
          </div>
        </div>

        {/* Actions Card */}
        <div style={{
          background: 'white',
          borderRadius: '16px',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
          padding: '24px',
        }}>
          <h3 style={{
            fontSize: '18px',
            fontWeight: 600,
            color: '#222222',
            margin: '0 0 20px 0',
          }}>
            Actions du compte
          </h3>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '12px',
          }}>
            <button
              onClick={() => navigate('/messages')}
              style={{
                padding: '14px 20px',
                background: '#DC2626',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '15px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
              }}
              onMouseEnter={(e) => {
                e.target.style.background = '#B91C1C'
                e.target.style.transform = 'translateY(-1px)'
                e.target.style.boxShadow = '0 4px 12px rgba(220, 38, 38, 0.3)'
              }}
              onMouseLeave={(e) => {
                e.target.style.background = '#DC2626'
                e.target.style.transform = 'translateY(0)'
                e.target.style.boxShadow = 'none'
              }}
            >
              <span>💬</span>
              <span>Mes messages</span>
            </button>

            {user.role !== 'EXPERT' && (
              <button
                onClick={() => navigate('/favorites')}
                style={{
                  padding: '14px 20px',
                  background: '#10B981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '15px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = '#059669'
                  e.target.style.transform = 'translateY(-1px)'
                  e.target.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.3)'
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = '#10B981'
                  e.target.style.transform = 'translateY(0)'
                  e.target.style.boxShadow = 'none'
                }}
              >
                <span>❤️</span>
                <span>Mes favoris</span>
              </button>
            )}

            <button
              onClick={handleLogout}
              style={{
                padding: '14px 20px',
                background: '#EF4444',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '15px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
              }}
              onMouseEnter={(e) => {
                e.target.style.background = '#DC2626'
                e.target.style.transform = 'translateY(-1px)'
                e.target.style.boxShadow = '0 4px 12px rgba(239, 68, 68, 0.3)'
              }}
              onMouseLeave={(e) => {
                e.target.style.background = '#EF4444'
                e.target.style.transform = 'translateY(0)'
                e.target.style.boxShadow = 'none'
              }}
            >
              <span>🚪</span>
              <span>Déconnexion</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function InfoField({ label, value, icon }) {
  return (
    <div style={{
      marginBottom: '16px',
      paddingBottom: '16px',
      borderBottom: '1px solid #E5E7EB',
    }}>
      <div style={{
        fontSize: '12px',
        fontWeight: 600,
        color: '#6B7280',
        marginBottom: '6px',
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
      }}>
        {label}
      </div>
      <div style={{
        fontSize: '15px',
        color: '#222222',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
      }}>
        <span>{icon}</span>
        <span>{value}</span>
      </div>
    </div>
  )
}
