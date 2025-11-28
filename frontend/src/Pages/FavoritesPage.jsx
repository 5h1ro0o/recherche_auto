import React from 'react'
import { Link } from 'react-router-dom'
import useSWR from 'swr'
import { getFavorites } from '../services/favorites'

export default function FavoritesPage() {
  const { data: vehicles, error, mutate } = useSWR('/favorites/me', getFavorites)

  if (error) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
        padding: '80px 20px',
      }}>
        <div style={{
          maxWidth: '600px',
          margin: '0 auto',
          textAlign: 'center',
          background: 'white',
          borderRadius: '16px',
          padding: '40px',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
        }}>
          <div style={{ fontSize: '64px', marginBottom: '20px' }}>⚠️</div>
          <h3 style={{ fontSize: '24px', color: '#222222', marginBottom: '12px' }}>
            Erreur de chargement
          </h3>
          <p style={{ color: '#6B7280' }}>
            Impossible de charger vos favoris. Veuillez réessayer plus tard.
          </p>
        </div>
      </div>
    )
  }

  if (!vehicles) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
        padding: '80px 20px',
      }}>
        <div style={{
          maxWidth: '600px',
          margin: '0 auto',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔄</div>
          <p style={{ color: '#6B7280', fontSize: '18px' }}>Chargement de vos favoris...</p>
        </div>
      </div>
    )
  }

  if (vehicles.length === 0) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
        padding: '80px 20px',
      }}>
        <div style={{
          maxWidth: '600px',
          margin: '0 auto',
          textAlign: 'center',
          background: 'white',
          borderRadius: '16px',
          padding: '60px 40px',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
        }}>
          <div style={{ fontSize: '80px', marginBottom: '24px' }}>❤️</div>
          <h2 style={{
            fontSize: '32px',
            fontWeight: 700,
            color: '#222222',
            margin: '0 0 16px 0',
          }}>
            Mes Favoris
          </h2>
          <p style={{
            fontSize: '18px',
            color: '#6B7280',
            margin: '0 0 32px 0',
          }}>
            Vous n'avez pas encore de favoris
          </p>
          <Link
            to="/search"
            style={{
              display: 'inline-block',
              padding: '14px 32px',
              background: '#DC2626',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: 600,
              transition: 'all 0.2s',
              boxShadow: '0 4px 12px rgba(220, 38, 38, 0.3)',
            }}
            onMouseEnter={(e) => {
              e.target.style.background = '#B91C1C'
              e.target.style.transform = 'translateY(-2px)'
              e.target.style.boxShadow = '0 8px 24px rgba(220, 38, 38, 0.4)'
            }}
            onMouseLeave={(e) => {
              e.target.style.background = '#DC2626'
              e.target.style.transform = 'translateY(0)'
              e.target.style.boxShadow = '0 4px 12px rgba(220, 38, 38, 0.3)'
            }}
          >
            🔍 Rechercher des véhicules
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
      paddingBottom: '60px',
    }}>
      {/* Header Section */}
      <div style={{
        background: 'linear-gradient(135deg, #DC2626 0%, #DC2626 100%)',
        color: 'white',
        padding: '60px 20px',
        textAlign: 'center',
        marginBottom: '40px',
      }}>
        <h1 style={{
          fontSize: '42px',
          fontWeight: 700,
          margin: '0 0 16px 0',
          lineHeight: 1.2,
        }}>
          ❤️ Mes Favoris
        </h1>
        <p style={{
          fontSize: '18px',
          margin: 0,
          opacity: 0.95,
        }}>
          {vehicles.length} véhicule{vehicles.length > 1 ? 's' : ''} sauvegardé{vehicles.length > 1 ? 's' : ''}
        </p>
      </div>

      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 20px',
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '24px',
        }}>
          {vehicles.map((v) => (
            <Link
              key={v.id}
              to={`/vehicle/${v.id}`}
              state={{ vehicle: v }}
              style={{
                display: 'block',
                background: 'white',
                borderRadius: '12px',
                padding: '20px',
                textDecoration: 'none',
                color: 'inherit',
                boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                border: '1px solid #EEEEEE',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)'
                e.currentTarget.style.boxShadow = '0 12px 40px rgba(0,0,0,0.12)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = '0 1px 2px rgba(0,0,0,0.04)'
              }}
            >
              {/* Image */}
              {v.images && v.images.length > 0 ? (
                <div style={{
                  width: '100%',
                  height: '180px',
                  borderRadius: '8px',
                  overflow: 'hidden',
                  marginBottom: '16px',
                }}>
                  <img
                    src={v.images[0]}
                    alt={v.title}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                    }}
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/400x300?text=No+Image'
                    }}
                  />
                </div>
              ) : (
                <div style={{
                  width: '100%',
                  height: '180px',
                  borderRadius: '8px',
                  background: '#F9FAFB',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px',
                  fontSize: '64px',
                }}>
                  🚗
                </div>
              )}

              {/* Title */}
              <h3 style={{
                margin: '0 0 12px 0',
                fontSize: '18px',
                fontWeight: 600,
                color: '#222222',
                lineHeight: 1.3,
              }}>
                {v.title || `${v.make} ${v.model}`}
              </h3>

              {/* Price */}
              {v.price && (
                <div style={{
                  fontSize: '24px',
                  fontWeight: 700,
                  color: '#DC2626',
                  marginBottom: '12px',
                }}>
                  {typeof v.price === 'number'
                    ? v.price.toLocaleString('fr-FR')
                    : v.price}{' '}
                  €
                </div>
              )}

              {/* Details */}
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '12px',
                fontSize: '14px',
                color: '#6B7280',
              }}>
                {v.year && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span>📅</span>
                    <span>{v.year}</span>
                  </div>
                )}
                {v.mileage && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span>🛣️</span>
                    <span>
                      {typeof v.mileage === 'number'
                        ? v.mileage.toLocaleString('fr-FR')
                        : v.mileage}{' '}
                      km
                    </span>
                  </div>
                )}
                {v.fuel_type && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span>⛽</span>
                    <span>{v.fuel_type}</span>
                  </div>
                )}
              </div>

              {/* Location */}
              {v.location_city && (
                <div style={{
                  marginTop: '12px',
                  paddingTop: '12px',
                  borderTop: '1px solid #E5E7EB',
                  fontSize: '14px',
                  color: '#6B7280',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}>
                  <span>📍</span>
                  <span>{v.location_city}</span>
                </div>
              )}
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
