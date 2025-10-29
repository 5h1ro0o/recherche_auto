import React, { useState } from 'react'
import { Link } from 'react-router-dom'

// Composant principal Results enrichi
export default function EnrichedResults({ loading, results = [], total = 0, page = 1, onPageChange }) {
  const [quickViewVehicle, setQuickViewVehicle] = useState(null)

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔄</div>
        <p style={{ color: '#6a737d' }}>Chargement des résultats...</p>
      </div>
    )
  }

  if (!results || results.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 20px' }}>
        <div style={{ fontSize: '64px', marginBottom: '20px' }}>🔍</div>
        <h3 style={{ fontSize: '24px', color: '#24292e', marginBottom: '12px' }}>
          Aucun résultat trouvé
        </h3>
        <p style={{ color: '#6a737d', fontSize: '16px' }}>
          Essayez d'élargir vos critères de recherche
        </p>
      </div>
    )
  }

  const formatPrice = (price) => {
    if (!price) return 'Prix non spécifié'
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0
    }).format(price)
  }

  const formatMileage = (mileage) => {
    if (!mileage) return 'N/A'
    return new Intl.NumberFormat('fr-FR').format(mileage) + ' km'
  }

  return (
    <div>
      <div style={{ marginBottom: '16px', color: '#586069' }}>
        {total} résultat{total > 1 ? 's' : ''} trouvé{total > 1 ? 's' : ''}.
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {results.map((vehicle) => (
          <div
            key={vehicle.id}
            style={{
              border: '1px solid #e1e4e8',
              borderRadius: '8px',
              padding: '20px',
              backgroundColor: 'white',
              transition: 'box-shadow 0.2s, transform 0.2s',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)'
              e.currentTarget.style.transform = 'translateY(-2px)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = 'none'
              e.currentTarget.style.transform = 'translateY(0)'
            }}
          >
            <div style={{ display: 'flex', gap: '20px' }}>
              {/* Image du véhicule */}
              <div style={{ flexShrink: 0, width: '200px', height: '150px' }}>
                {vehicle.images && vehicle.images.length > 0 ? (
                  <img
                    src={vehicle.images[0]}
                    alt={vehicle.title || 'Véhicule'}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                      borderRadius: '6px'
                    }}
                    onError={(e) => {
                      e.target.style.display = 'none'
                    }}
                  />
                ) : (
                  <div
                    style={{
                      width: '100%',
                      height: '100%',
                      backgroundColor: '#f6f8fa',
                      borderRadius: '6px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '48px'
                    }}
                  >
                    🚗
                  </div>
                )}
              </div>

              {/* Informations du véhicule */}
              <div style={{ flex: 1 }}>
                <Link
                  to={`/vehicle/${vehicle.id}`}
                  style={{
                    fontSize: '20px',
                    fontWeight: 'bold',
                    color: '#0366d6',
                    textDecoration: 'none',
                    marginBottom: '8px',
                    display: 'block'
                  }}
                >
                  {vehicle.title || `${vehicle.make || ''} ${vehicle.model || ''}`}
                </Link>

                <div style={{ display: 'flex', gap: '16px', marginBottom: '12px', flexWrap: 'wrap' }}>
                  {vehicle.year && (
                    <span style={{ color: '#586069', fontSize: '14px' }}>
                      📅 {vehicle.year}
                    </span>
                  )}
                  {vehicle.mileage && (
                    <span style={{ color: '#586069', fontSize: '14px' }}>
                      🛣️ {formatMileage(vehicle.mileage)}
                    </span>
                  )}
                  {vehicle.fuel_type && (
                    <span style={{ color: '#586069', fontSize: '14px' }}>
                      ⛽ {vehicle.fuel_type}
                    </span>
                  )}
                  {vehicle.transmission && (
                    <span style={{ color: '#586069', fontSize: '14px' }}>
                      ⚙️ {vehicle.transmission}
                    </span>
                  )}
                </div>

                {vehicle.description && (
                  <p
                    style={{
                      color: '#586069',
                      fontSize: '14px',
                      lineHeight: '1.5',
                      marginBottom: '12px',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden'
                    }}
                  >
                    {vehicle.description}
                  </p>
                )}

                {vehicle.location_city && (
                  <div style={{ color: '#586069', fontSize: '14px', marginBottom: '8px' }}>
                    📍 {vehicle.location_city}
                  </div>
                )}
              </div>

              {/* Prix et actions */}
              <div style={{ textAlign: 'right', minWidth: '150px' }}>
                <div
                  style={{
                    fontSize: '24px',
                    fontWeight: 'bold',
                    color: '#28a745',
                    marginBottom: '16px'
                  }}
                >
                  {formatPrice(vehicle.price)}
                </div>

                <Link
                  to={`/vehicle/${vehicle.id}`}
                  style={{
                    display: 'inline-block',
                    padding: '10px 20px',
                    backgroundColor: '#0366d6',
                    color: 'white',
                    borderRadius: '6px',
                    textDecoration: 'none',
                    fontSize: '14px',
                    fontWeight: '600',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = '#0256c7'
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = '#0366d6'
                  }}
                >
                  Voir détails
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {total > 20 && onPageChange && (
        <div style={{ marginTop: '32px', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', gap: '8px', alignItems: 'center' }}>
            <button
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
              style={{
                padding: '8px 16px',
                border: '1px solid #e1e4e8',
                borderRadius: '6px',
                backgroundColor: page <= 1 ? '#f6f8fa' : 'white',
                color: page <= 1 ? '#959da5' : '#24292e',
                cursor: page <= 1 ? 'not-allowed' : 'pointer',
                fontWeight: '600'
              }}
            >
              ← Précédent
            </button>

            <span style={{ padding: '0 16px', color: '#586069' }}>
              Page {page} / {Math.ceil(total / 20)}
            </span>

            <button
              onClick={() => onPageChange(page + 1)}
              disabled={page >= Math.ceil(total / 20)}
              style={{
                padding: '8px 16px',
                border: '1px solid #e1e4e8',
                borderRadius: '6px',
                backgroundColor: page >= Math.ceil(total / 20) ? '#f6f8fa' : 'white',
                color: page >= Math.ceil(total / 20) ? '#959da5' : '#24292e',
                cursor: page >= Math.ceil(total / 20) ? 'not-allowed' : 'pointer',
                fontWeight: '600'
              }}
            >
              Suivant →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
