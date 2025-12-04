import React from 'react'
import { Link } from 'react-router-dom'
import useSWR from 'swr'
import { getFavorites } from '../services/favorites'

export default function FavoritesPage() {
  const { data: vehicles, error, mutate } = useSWR('/favorites/me', getFavorites)

  if (error) {
    return (
      <div className="app-main">
        <div style={{
          maxWidth: 'var(--container-md)',
          margin: '0 auto',
          textAlign: 'center'
        }}>
          <div className="card">
            <div className="card-body">
              <h3 style={{
                fontSize: '24px',
                color: 'var(--text-primary)',
                marginBottom: 'var(--space-3)',
                fontWeight: 'var(--font-weight-semibold)'
              }}>
                Erreur de chargement
              </h3>
              <p style={{ color: 'var(--text-secondary)' }}>
                Impossible de charger vos favoris. Veuillez réessayer plus tard.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!vehicles) {
    return (
      <div className="app-main">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p style={{ marginTop: 'var(--space-4)', color: 'var(--text-secondary)' }}>
            Chargement de vos favoris...
          </p>
        </div>
      </div>
    )
  }

  if (vehicles.length === 0) {
    return (
      <div className="app-main">
        <div style={{
          maxWidth: 'var(--container-md)',
          margin: '0 auto',
          textAlign: 'center'
        }}>
          <div className="card">
            <div className="card-body" style={{ padding: 'var(--space-16) var(--space-10)' }}>
              <h2 style={{
                fontSize: '32px',
                fontWeight: 'var(--font-weight-bold)',
                color: 'var(--text-primary)',
                margin: '0 0 var(--space-4) 0',
                letterSpacing: '-0.02em'
              }}>
                Mes Favoris
              </h2>
              <p style={{
                fontSize: '18px',
                color: 'var(--text-secondary)',
                margin: '0 0 var(--space-8) 0',
                fontWeight: 'var(--font-weight-medium)'
              }}>
                Vous n'avez pas encore de favoris
              </p>
              <Link
                to="/search"
                className="btn btn-primary"
                style={{
                  display: 'inline-block',
                  padding: 'var(--space-4) var(--space-8)',
                  fontSize: '16px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}
              >
                Rechercher des véhicules
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--gray-50)',
      paddingBottom: 'var(--space-16)'
    }}>
      {/* Header Section */}
      <div style={{
        background: 'var(--white)',
        color: 'var(--text-primary)',
        padding: 'var(--space-16) var(--space-6)',
        textAlign: 'center',
        marginBottom: 'var(--space-10)',
        borderBottom: '1px solid var(--border-light)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Gloss overlay */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '200px',
          background: 'var(--gloss-overlay)',
          pointerEvents: 'none'
        }} />

        <h1 style={{
          fontSize: '48px',
          fontWeight: 'var(--font-weight-bold)',
          margin: '0 0 var(--space-4) 0',
          lineHeight: 1.1,
          letterSpacing: '-0.02em',
          position: 'relative',
          zIndex: 1
        }}>
          Mes Favoris
        </h1>
        <p style={{
          fontSize: '18px',
          margin: 0,
          color: 'var(--text-secondary)',
          fontWeight: 'var(--font-weight-medium)',
          position: 'relative',
          zIndex: 1
        }}>
          {vehicles.length} véhicule{vehicles.length > 1 ? 's' : ''} sauvegardé{vehicles.length > 1 ? 's' : ''}
        </p>
      </div>

      <div style={{
        maxWidth: 'var(--container-2xl)',
        margin: '0 auto',
        padding: '0 var(--space-5)'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: 'var(--space-6)'
        }}>
          {vehicles.map((v) => (
            <Link
              key={v.id}
              to={`/vehicle/${v.id}`}
              state={{ vehicle: v }}
              style={{
                display: 'block',
                background: 'var(--white)',
                padding: 'var(--space-5)',
                textDecoration: 'none',
                color: 'inherit',
                boxShadow: 'var(--shadow-gloss-sm)',
                border: '1px solid var(--border-light)',
                transition: 'all var(--transition-base)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)'
                e.currentTarget.style.boxShadow = 'var(--shadow-gloss-lg)'
                e.currentTarget.style.borderColor = 'var(--border-medium)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = 'var(--shadow-gloss-sm)'
                e.currentTarget.style.borderColor = 'var(--border-light)'
              }}
            >
              {/* Image */}
              {v.images && v.images.length > 0 ? (
                <div style={{
                  width: '100%',
                  height: '180px',
                  overflow: 'hidden',
                  marginBottom: 'var(--space-4)',
                  background: 'var(--gray-100)'
                }}>
                  <img
                    src={v.images[0]}
                    alt={v.title}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover'
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
                  background: 'var(--gray-100)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: 'var(--space-4)',
                  fontSize: '14px',
                  color: 'var(--text-muted)',
                  fontWeight: 'var(--font-weight-medium)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  Pas d'image
                </div>
              )}

              {/* Title */}
              <h3 style={{
                margin: '0 0 var(--space-3) 0',
                fontSize: '18px',
                fontWeight: 'var(--font-weight-semibold)',
                color: 'var(--text-primary)',
                lineHeight: 1.3,
                letterSpacing: '-0.01em'
              }}>
                {v.title || `${v.make} ${v.model}`}
              </h3>

              {/* Price */}
              {v.price && (
                <div style={{
                  fontSize: '24px',
                  fontWeight: 'var(--font-weight-bold)',
                  color: 'var(--red-accent)',
                  marginBottom: 'var(--space-3)',
                  letterSpacing: '-0.01em'
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
                gap: 'var(--space-3)',
                fontSize: '13px',
                color: 'var(--text-secondary)',
                fontWeight: 'var(--font-weight-medium)'
              }}>
                {v.year && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                    <span style={{ fontWeight: 'var(--font-weight-semibold)' }}>Année:</span>
                    <span>{v.year}</span>
                  </div>
                )}
                {v.mileage && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                    <span style={{ fontWeight: 'var(--font-weight-semibold)' }}>KM:</span>
                    <span>
                      {typeof v.mileage === 'number'
                        ? v.mileage.toLocaleString('fr-FR')
                        : v.mileage}
                    </span>
                  </div>
                )}
                {v.fuel_type && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                    <span style={{ fontWeight: 'var(--font-weight-semibold)' }}>Carburant:</span>
                    <span>{v.fuel_type}</span>
                  </div>
                )}
              </div>

              {/* Location */}
              {v.location_city && (
                <div style={{
                  marginTop: 'var(--space-3)',
                  paddingTop: 'var(--space-3)',
                  borderTop: '1px solid var(--border-light)',
                  fontSize: '13px',
                  color: 'var(--text-secondary)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-2)',
                  fontWeight: 'var(--font-weight-medium)'
                }}>
                  <span style={{ fontWeight: 'var(--font-weight-semibold)' }}>Localisation:</span>
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
